import os
import pickle
from typing import Any
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone

from langchain_core.messages import AIMessageChunk
from langchain.messages import AnyMessage, RemoveMessage
from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import (
    dynamic_prompt,
    ModelRequest,
    before_model,
    after_model,
    SummarizationMiddleware,
)
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.runtime import Runtime
from langgraph.checkpoint.mongodb import MongoDBSaver
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from pymongo import MongoClient
from dotenv import load_dotenv
from tools import data_collector_agent_tools, data_analyst_tools
from prompts import (
    data_collector_system_prompt,
    analyst_system_prompt,
    supervisor_system_prompt,
)

load_dotenv()

model = ChatOpenAI(
    model="gpt-4.1-mini-2025-04-14",
    temperature=0,
    api_key=os.getenv("openai"),
    streaming=True,
)
#
# model = ChatOllama(
#     model="llama3.2:latest",
#     base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
#     validate_model_on_init=True,
#     temperature=0.8,
#     num_predict=256,
#     streaming=True
#     # other params ...
# )
Mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
database_name = "chat_db"

mongo_client = MongoClient(Mongo_uri)
db = mongo_client[database_name]
chat_collection = db["chat_history"]


@dataclass
class Context:
    user_name: str



@dynamic_prompt
def dynamic_system_prompt(request: ModelRequest) -> str:
    user_name = request.runtime.context.user_name
    return f"You are a helpful assistant. Address the user as {user_name}."


# -------------------------------------------------------
# Hooks
# -------------------------------------------------------
@before_model
def log_before_model(state: AgentState, runtime: Runtime[Context]) -> None:
    print(f"Processing request for user: {runtime.context.user_name}")


@after_model
def log_after_model(state: AgentState, runtime: Runtime[Context]) -> None:
    print(f"Completed request for user: {runtime.context.user_name}")


@before_model
def trim_messages(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """Keep only the last few messages to fit context window."""
    messages = state["messages"]
    if len(messages) <= 3:
        return None  # No changes needed

    first_msg = messages[0]
    recent_messages = messages[-3:] if len(messages) % 2 == 0 else messages[-4:]
    new_messages = [first_msg] + recent_messages

    return {
        "messages": [
            RemoveMessage(id=REMOVE_ALL_MESSAGES),
            *new_messages
        ]
    }


# After model hook
@after_model
def log_after_model(state: AgentState, runtime: Runtime[Context]) -> dict | None:
    print(f"Completed request for user: {runtime.context.user_name}")
    return None


@after_model
def delete_old_messages(state: AgentState, runtime: Runtime) -> dict | None:
    """Remove old messages to keep conversation manageable."""
    messages = state["messages"]
    if len(messages) > 2:
        # remove the earliest two messages
        return {"messages": [RemoveMessage(id=m.id) for m in messages[:2]]}
    return None


# -------------------------------------------------------
# Agents
# -------------------------------------------------------
data_collector_agent = create_agent(
    model=model,
    tools=data_collector_agent_tools,
    middleware=[dynamic_system_prompt, log_before_model, log_after_model],
    context_schema=Context,
    system_prompt=data_collector_system_prompt,
)

data_analytics_agent = create_agent(
    model=model,
    tools=data_analyst_tools,
    middleware=[dynamic_system_prompt, log_before_model, log_after_model],
    context_schema=Context,
    system_prompt=analyst_system_prompt,
)


# -------------------------------------------------------
# Tools used by supervisor
# -------------------------------------------------------
@tool
def collect_market_data(request: str) -> str:
    """
    Collect stock/market related data.
    Use this when the user asks for stock prices, fundamentals, news, indicators, company info, or raw financial data.
    """
    result = data_collector_agent.invoke({
        "messages": [{"role": "user", "content": request}]
    })
    print("called this tool collect_market_data")
    return result["messages"][-1].content


@tool
def analyze_market_data(request: str) -> str:
    """
    Analyze already collected stock data.
    Use this for predictions, insights, risk analysis, patterns, or summaries.
    """
    result = data_analytics_agent.invoke({
        "messages": [{"role": "user", "content": request}]
    })
    print("called this tool analyze_market_data")
    return result["messages"][-1].content


# -------------------------------------------------------
# Supervisor runner (streaming)
# -------------------------------------------------------
class SupervisorRunner:
    def __init__(self, input_text: str, user_name: str, session_id: str):
        self.input_text = input_text
        self.user_name = user_name
        self.session_id = session_id
        self.final_text = ""

    def _get_config(self):
        return {
            "configurable": {
                "thread_id": self.session_id,
                "checkpoint_ns": "chat",
            }
        }

    def _run_graph_sync(self):
        with MongoDBSaver.from_conn_string(
            conn_string=Mongo_uri,
            db_name=database_name,
        ) as checkpointer:

            supervisor_agent = create_agent(
                model=model,
                tools=[collect_market_data, analyze_market_data],
                middleware=[dynamic_system_prompt, log_before_model, log_after_model],
                context_schema=Context,
                system_prompt=supervisor_system_prompt,
                checkpointer=checkpointer,
            )

            for event in supervisor_agent.stream(
                {"messages": [("human", self.input_text)]},
                context=Context(user_name=self.user_name),
                config=self._get_config(),
                stream_mode="messages",
            ):
                msg, _ = event

                if isinstance(msg, AIMessageChunk) and msg.content:
                    self.final_text += msg.content
                    yield msg.content

            # Save history once completed
            self._save_chat_history(self.final_text)

    # ---------------------------------------------------
    # Save chat history (MongoDB)
    # ---------------------------------------------------
    def _save_chat_history(self, txt_only: str):
        try:
            formatted_input_time = datetime.now(timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%S"
            )
            formatted_answer_time = datetime.now(timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%S"
            )
            chat_date = datetime.now().strftime("%Y-%m-%d")

            message_entry = {
                "prompt": self.input_text,
                "prompt_timestamp": formatted_input_time,
                "answer": txt_only,
                "answer_timestamp": formatted_answer_time,
            }

            chat_collection.update_one(
                {"session_id": self.session_id},
                {
                    "$push": {f"messages.{chat_date}": message_entry},
                    "$setOnInsert": {
                        "session_id": self.session_id,
                        "user_name": self.user_name,
                        "created_at": formatted_input_time,
                    },
                },
                upsert=True,
            )

            print(f"Chat history saved for session {self.session_id}")

        except Exception as e:
            print(f"Error saving chat history: {e}")
