# MCP Agent Demo: Your First MCP Agent

[中文文档](https://github.com/whitejoce/mcp_agent/blob/main/README_CN.md)

## 🔥 Project Overview
This project is a simple Agent example based on [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) to demonstrate the basic functionality of an MCP Host.

It follows the implementation approach of the MCP Host Agent from the [DIY-your-AI-agent](https://github.com/whitejoce/DIY-your-AI-agent) project, aimed at helping you quickly understand and get started with MCP application development.

<img src="https://github.com/whitejoce/mcp_agent/blob/main/img/example.png" alt="MCP Agent Demo Example">

---

## 🚀 Quick Start

### 1️⃣ Prerequisites
Ensure you have **Python 3.7+** installed. Then, install the necessary libraries:

```bash
pip install openai rich fastmcp
```
* `openai`: For interacting with LLM APIs.
* `rich`: For displaying rich text in the terminal.
* `fastmcp`: Python implementation of MCP.

### 2️⃣ API Configuration
Edit the `agent_en.py` file and fill in your configuration:

```python
API_CONFIG = {
   "url": "YOUR_LLM_API_BASE_URL",          # Replace with your LLM API base URL
   "api_key": "YOUR_LLM_API_KEY",           # Replace with your LLM API key
   "model": "Qwen/Qwen2.5-7B-Instruct",     # Specify the LLM model to use
   "MCP_Server": "http://127.0.0.1:8000/sse" # Your MCP server address (if using local server.py)
}
```
**Note:** The `MCP_Server` address needs to match the MCP Server run in the next step.

### 3️⃣ Run MCP Server
This demo includes a simple MCP Server implementation for demonstration. Run in your terminal:
> HTTP with SSE transport

```bash
$ python ./mcp_demo/server.py
```
You'll see output like this, indicating the server has started successfully:
```
[04/27/25 12:00:00] INFO     Starting server "Demo"...                                                                                                                 server.py:262
INFO:     Started server process [21112]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### 4️⃣ Run the Agent
In another terminal window, run the Agent script:

```bash
$ python agent.py
```
Now, the Agent will connect to the MCP Server and interact with the LLM through it.

---

## 💡 How to Improve?

Want to make your Agent smarter and more powerful? Consider these approaches:

1. **Direct AI Conversations** 🤖
   * Talk directly with the model in the terminal to iterate on your ideas.
   * Try asking: "How can I give my Agent stronger decision-making abilities?" or "How can I optimize my terminal assistant experience?"

2. **Explore Model Context Protocol (MCP)** 🏗️
   * MCP is an open protocol for seamless integration between LLMs and external data sources/tools.
   * It helps models access richer context information to generate more accurate responses.
   * Study MCP's core concepts like `Resources`, `Tools`, and `Prompts` to enhance your Agent's capabilities.
   * **Resources:**
      * [MCP Official Introduction](https://modelcontextprotocol.io/introduction)
      * [FastMCP Documentation](https://gofastmcp.com/getting-started/welcome)

3. **Integrate More Tools** 🛠️
   * Follow MCP specifications to add capabilities like external API calls, local script execution, database access, etc.

4. **Leverage Resources** 📚
   * Provide file contents, web information, or other dynamic data as context to the LLM through MCP.

---

## 📜 License

This project is under the **MIT License**. Feel free to use, modify, and distribute.

## 🤝 Contributing

Issues and Pull Requests welcome! If you have improvement suggestions or find bugs, please let us know.