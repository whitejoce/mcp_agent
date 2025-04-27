# MCP Agent Demo: 你的第一个 MCP Agent

## 🔥 项目简介
本项目是一个基于 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) 的简单 Agent 示例，用于演示 MCP Host 的基本功能。

它基于 [DIY-your-AI-agent](https://github.com/whitejoce/DIY-your-AI-agent) 项目中 MCP Host 端 Agent 的实现方式，旨在帮助你快速理解和上手 MCP 应用开发。

<img src="https://github.com/whitejoce/mcp_agent/blob/main/img/example.png" alt="MCP Agent Demo Example">

---

## 🚀 快速开始

### 1️⃣ 环境准备
确保你已安装 **Python 3.7+**。然后，安装必要的库：

```bash
pip install openai rich fastmcp
```
*   `openai`: 用于与 LLM API 交互。
*   `rich`: 用于在终端显示富文本。
*   `fastmcp`: MCP 的 Python 实现库。

### 2️⃣ 配置 API
编辑 `agent.py` 文件，填入你的配置信息：

```python
API_CONFIG = {
   "url": "YOUR_LLM_API_BASE_URL",          # 替换为你的 LLM API 基础 URL
   "api_key": "YOUR_LLM_API_KEY",           # 替换为你的 LLM API 密钥
   "model": "Qwen/Qwen2.5-7B-Instruct",     # 指定要使用的 LLM 模型
   "MCP_Server": "http://127.0.0.1:8000/sse" # 你的 MCP 服务器地址 (如果使用本地 server.py)
}
```
**注意:** `MCP_Server` 地址需要与下一步运行的 MCP Server 匹配。

### 3️⃣ 运行 MCP Server
此 Demo 包含一个简单的 MCP Server 实现，用于演示。在终端中运行：
> 通信方式：Server-Sent Events (SSE)

```bash
$ python ./mcp_demo/server.py
```
你会看到类似以下的输出，表示服务器已成功启动：
```
[04/27/25 12:00:00] INFO     Starting server "Demo"...                                                                                                                 server.py:262
INFO:     Started server process [21112]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### 4️⃣ 运行 Agent
在另一个终端窗口中，运行 Agent 脚本：

```bash
$ python agent.py
```
现在，Agent 会连接到 MCP Server，并通过它与 LLM 进行交互。

---

## 💡 如何做得更好？

想让你的 Agent 更智能、功能更强大吗？可以考虑以下方向：

1.  **直接与 AI 对话** 🤖
   *   在终端与大模型直接交流，迭代你的想法。
   *   尝试提问：“如何让 Agent 具备更强的自主决策能力？”或“怎样优化我的终端助手交互体验？”

2.  **深入探索 Model Context Protocol (MCP)** 🏗️
   *   MCP 是一个开放协议，旨在实现大型语言模型 (LLM) 与外部数据源和工具的无缝集成。
   *   通过标准化交互方式，MCP 帮助模型获取更丰富的上下文信息，生成更准确、相关的响应。
   *   研究 MCP 定义的 `Resources`、`Tools`、`Prompts` 等核心概念，充分利用它们来增强 Agent 的能力。
   *   **推荐资源:**
      *   [MCP 官方介绍](https://modelcontextprotocol.io/introduction)
      *   [FastMCP 文档](https://gofastmcp.com/getting-started/welcome)

3.  **集成更多工具 (Tools)** 🛠️
   *   根据 MCP 规范，为 Agent 添加调用外部 API、执行本地脚本、访问数据库等能力。

4.  **利用资源 (Resources)** 📚
   *   通过 MCP 向 LLM 提供文件内容、网页信息或其他动态数据作为上下文。

---

## 📜 License

本项目采用 **MIT 许可证**。欢迎自由使用、修改和分发。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！如果你有任何改进建议或发现了 Bug，请随时提出。