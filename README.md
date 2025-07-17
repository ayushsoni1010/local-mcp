[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/ayushsoni1010-sqlite-mcp-agent-badge.png)](https://mseep.ai/app/ayushsoni1010-sqlite-mcp-agent)

# Local MCP Client Demo

This project demonstrates a fully local Model Context Protocol (MCP) client using:

- **SQLite** via Python `sqlite3`
- **FastMCP** (`mcp-server`) for tool management
- **DeepSeek-R1** LLM hosted locally via **Ollama**
- **LlamaIndex** for building an MCP-powered agent

## 📦 Requirements

Ensure you have the following installed:

- Python 3.8+
- [Ollama CLI](https://ollama.ai/docs) (for DeepSeek-R1)
- System packages:

  ```bash
  pip install -r requirements.txt
  ```

## 🛠️ Files Overview

- `server.py` — MCP server exposing `add_data` & `read_data` tools backed by SQLite
- `ollama_client.py` — Async agent setup using Ollama + LlamaIndex
- `chat_interface.py` — CLI wrapper to chat with the agent
- `requirements.txt` — Python dependencies

## 🚀 Setup & Running

1. **Start the MCP Server**

   ```bash
   # Initialize database and run in SSE mode
   python server.py --server_type sse
   ```

2. **Launch Ollama & DeepSeek-R1**

   ```bash
   ollama pull deepseek-r1
   ollama run deepseek-r1
   ```

3. **Install Python Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Chat Client**

   ```bash
   python chat_interface.py
   ```

   Type your queries (e.g., `add_data(...)` or natural questions) and see the agent invoke tools and respond.

## 🎯 Best Practices

- **Tool Design**: Keep tools focused (single responsibility) and clearly document inputs/outputs.
- **Error Handling**: Catch and log exceptions in tool implementations to avoid silent failures.
- **Security**: Avoid executing raw SQL when possible; use parameterized queries for production.
- **Extensibility**: Add new MCP tools by decorating with `@mcp.tool()` and exposing via `list_tools`.

## 📝 Next Steps

- Integrate additional data sources (e.g., external APIs).
- Deploy on Lightning AI for scalable hosting.
- Enhance agent prompts and caching strategy for performance.

---

_Demo built with ❤️ for fully local, context-aware agents!_
