# 📈 Stock Market Multi-Agent Analysis System

A powerful **Stock Market Analysis & Chatbot System** built using **LangChain** and **LangGraph**, featuring a **multi-agent architecture**, real-time Indian stock market data, and a clean **Streamlit** UI.
The system supports both **OpenAI** and **Ollama** LLMs, and uses **MongoDB** for chat persistence and agent checkpointing.

---

## 🚀 Features

* 🤖 **Multi-Agent Chatbot System**

  * Built with **LangChain** + **LangGraph**
  * Supervisor + task-specific agents
  * Streaming responses

* 📊 **Real-Time Indian Stock Market Data**

  * Powered by: [Indian Stock Market API](https://indianapi.in/indian-stock-market)
  * Fetches live stock prices, trends, 52-week highs/lows, etc.

* 🧠 **LLM Support**

  * Choose between:

    * 🔑 **OpenAI API**
    * 🦙 **Ollama (Local LLMs)**

* 💬 **Chat Persistence**

  * MongoDB used for:

    * Chat history storage
    * Agent checkpointing
    * Conversation recovery

* 🖥️ **Streamlit Interface**

  * Interactive chatbot UI
  * Clean and simple stock analysis dashboard

* 🐳 **Docker Support**

  * Run everything using `docker-compose`
  * MongoDB + Ollama + App containers

---

## 🏗️ Tech Stack

| Component     | Technology              |
| ------------- | ----------------------- |
| UI            | Streamlit               |
| Agents        | LangChain, LangGraph    |
| LLMs          | OpenAI API / Ollama     |
| Database      | MongoDB                 |
| Stock Data    | Indian Stock Market API |
| Orchestration | Docker, Docker Compose  |

---

## 📂 Project Structure

```
stock_market_analyser_using_langchain/
├── app.py                  # Streamlit UI entry point
├── agent.py                # Multi-agent system (LangChain + LangGraph)
├── tools.py                # Tools for stock market API interactions
├── prompts.py              # System and agent prompts
├── utils.py                # Helper and utility functions
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Docker services (App, MongoDB, Ollama)
├── .gitignore              # Git ignored files
└── README.md               # Project documentation
```

---

## 🔑 Environment Variables

Create a `.env` file:

```env
# MongoDB
MONGO_URI="mongodb://localhost:27017"

# Ollama
OLLAMA_BASE_URL="http://localhost:11434"

# Indian Stock Market API
INDIAN_API_KEY="your_indianapi_key"

# If using OpenAI
OPENAI_API_KEY="your_openai_api_key"
```

You can use **either OpenAI or Ollama**:

* If `OPENAI_API_KEY` exists → OpenAI will be used
* Else Ollama will be used via `OLLAMA_BASE_URL`

---

## 🐳 Run with Docker (Recommended)

Make sure Docker & Docker Compose are installed.

```bash
docker compose up --build
```

This will start:

* MongoDB
* Ollama
* Streamlit App

Then open:

```
http://localhost:8501
```

---

## 🧪 Run Locally (Virtual Environment)

1. Create virtual environment:

```bash
python -m venv venv
source venv/bin/activate      # Linux / Mac
venv\Scripts\activate         # Windows
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start MongoDB & Ollama manually:

```bash
# MongoDB
mongod

# Ollama
ollama serve
```

4. Run the app:

```bash
streamlit run app.py
```

---

## 💡 Example Usage

Ask the bot:

* “Analyze TCS stock and give me risks”
* “Show today’s trending stocks”
* “Compare Infosys vs Wipro”
* “Which stock is near its 52-week high?”

The supervisor agent automatically routes your query to the right agent:

* Data Collector
* Analyzer
* Financial Summary Agent

---

## 🔐 Persistence & Checkpointing

MongoDB is used for:

* Chat history
* Agent memory
* Conversation recovery
* Multi-agent workflow checkpoints

This ensures:

> No chat is lost, even if the app restarts.

---

## 📌 Why This Project?

This project demonstrates:

* Real-world **AI agent orchestration**
* **Financial domain AI application**
* Production-style persistence with MongoDB
* Flexible LLM backends (Cloud + Local)
* Docker-first deployment approach

Perfect for:

* AI portfolio projects
* FinTech experiments
* Multi-agent research
* LangGraph learning reference

---

## ⭐ If you like this project

Give it a ⭐ on GitHub and feel free to fork & extend it!
