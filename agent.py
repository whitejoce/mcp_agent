#!/usr/bin/env python
# _*_coding: utf-8 _*_
# Coder: Whitejoce

import re, json
import subprocess
import asyncio

from openai import OpenAI

from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.markdown import Markdown

from fastmcp import Client
from fastmcp.client.transports import (
    SSETransport
)

# API 配置字典
API_CONFIG = {
    "url": "",  # 你的LLM API基础URL
    "api_key": "",  # 你的LLM API密钥
    "model": "Qwen/Qwen2.5-7B-Instruct", # 使用的LLM模型名称
    "MCP_Server": "http://127.0.0.1:8000/sse"  # 你的MCP服务器地址
}

# 验证API配置是否已填写
assert (
    API_CONFIG["url"] != "your_url" and API_CONFIG["api_key"] != ""
), "请填写正确的url和api_key"

# 系统提示词，指导LLM如何响应和使用工具
SYSTEM_PROMPT = """
你是一个智能终端助手，需要根据用户请求选择合适的操作方式，必须严格输出JSON格式，无Markdown。

规则：
1. 当用户意图可以通过内置工具（tools）完成时，优先调用工具，并生成调用指令和需要的参数。
2. 如果不需要操作，仅直接回复答案。

JSON格式必须符合：
- 显示工具示例：
{
    "action": "show_tools",
    "explain": "列出所有可用工具"
}
- 调用工具示例：
{
  "action": "call_tool",
  "tool_name": "list_files",
  "parameters": {
    "path": "/home/user"
  }
}
- 直接回复示例：
{
  "action": "direct_reply",
  "content": "这是直接回复的内容"
}
"""

# 初始化Rich Console
console = Console()

# 初始化OpenAI客户端
client = OpenAI(api_key=API_CONFIG["api_key"], base_url=API_CONFIG["url"])

# 初始化聊天历史，包含系统提示词
payload = [{"role": "system", "content": SYSTEM_PROMPT}]


def get_chat_response(client, payload):
    """
    调用LLM API获取聊天响应。

    Args:
        client: OpenAI客户端实例。
        payload: 包含聊天历史的列表。

    Returns:
        tuple: 包含回复内容和思考过程内容的元组 (reply_content, reasoning_content)。
    """
    # 调用LLM API，使用流式传输获取响应
    response = client.chat.completions.create(
        model=API_CONFIG["model"], messages=payload, stream=True
    )
    reply_chunk, reasoning_chunk = [], [] # 用于存储回复和思考过程的片段
    full_reply = "" # 用于拼接完整的回复内容
    has_reasoning = False # 标记是否有思考过程内容
    # 显示"思考中..."状态
    with console.status("[bold green]思考中...[/bold green]") as status:
        # 遍历响应流中的每个块
        for chunk in response:
            # 处理回复内容
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                reply_chunk.append(content)
                full_reply += content

            # 处理思考过程内容 (如果存在)
            # 注意: 'reasoning_content' 是一个假设的字段，实际API可能不同
            if hasattr(chunk.choices[0].delta, 'reasoning_content') and chunk.choices[0].delta.reasoning_content:
                has_reasoning = True
                reasoning_content = chunk.choices[0].delta.reasoning_content
                reasoning_chunk.append(reasoning_content)
                status.stop() # 停止"思考中..."状态显示
                console.print(reasoning_content, end="") # 实时打印思考过程

    # 如果有思考过程内容，打印一个换行符
    if has_reasoning:
        print()
    # 返回拼接好的回复内容和思考过程内容
    return "".join(reply_chunk), "".join(reasoning_chunk)

async def get_tools_list():
    """
    异步连接MCP服务器并获取可用工具列表。

    Returns:
        list: 包含工具信息的列表，如果失败则返回空列表或引发异常。
    """
    # 使用SSETransport连接MCP服务器
    async with Client(SSETransport(API_CONFIG["MCP_Server"])) as client:
        # 调用MCP客户端的list_tools方法
        tools = await client.list_tools()
        return tools

async def call_tool(tool_name, parameters):
    """
    异步连接MCP服务器并调用指定的工具。

    Args:
        tool_name (str): 要调用的工具名称。
        parameters (dict): 调用工具所需的参数。

    Returns:
        Any: 工具执行的结果。如果调用失败，返回错误信息字符串。
    """
    # 使用SSETransport连接MCP服务器
    async with Client(SSETransport(API_CONFIG["MCP_Server"])) as client:
        try:
            # 调用MCP客户端的call_tool方法
            result = await client.call_tool(tool_name, parameters)
            return result
        except Exception as e:
            # 捕获调用过程中的异常
            return f"调用工具失败: {str(e)}"


async def main():
    """
    主异步函数，运行聊天交互循环。
    """
    rejudge = False # 是否需要让LLM重新生成响应的标志
    rejudge_count = 0 # 重试次数计数器
    # 主循环，持续接收用户输入并处理
    while True:
        try:
            # 如果不需要重新判断，则获取用户输入
            if not rejudge:
                rejudge = False # 重置重试标志
                # 使用Rich Prompt获取用户输入
                user_input = Prompt.ask("[bold blue]Smart_Shell[/bold blue]")

                # 处理退出命令
                if user_input.lower() in ["/quit", "exit", "quit"]:
                    console.print("[yellow]再见！[/yellow]")
                    break

                # 将用户输入添加到聊天历史
                payload.append({"role": "user", "content": user_input})

            # 调用LLM获取响应和思考过程
            reply, reasoning = get_chat_response(client, payload)

            try:
                # 尝试从Markdown代码块中提取JSON
                pattern = re.compile(r"```json\n(.*?)\n```", re.S)
                if pattern.search(reply):
                    reply = pattern.findall(reply)[0]
                # 解析LLM返回的JSON字符串
                command = json.loads(reply)
                # 将LLM的有效回复添加到聊天历史
                payload.append({"role": "assistant", "content": reply})
                rejudge = False # 解析成功，重置重试标志
                rejudge_count = 0 # 重置重试计数器

                # 根据解析出的action执行相应操作
                if command["action"] == "show_tools":
                    try:
                        # 获取工具列表
                        tools = await get_tools_list()
                        content = f"发现 {len(tools)} 个可用工具：\n\n" # 用于添加到聊天历史的文本

                        # 使用Rich Panel显示工具数量
                        console.print(
                            Panel(
                                f"[bold green]发现 {len(tools)} 个可用工具[/bold green]",
                                title="工具列表",
                                border_style="green",
                            )
                        )

                        # 遍历并显示每个工具的详细信息
                        for index, tool in enumerate(tools, 1):
                            tool_name = getattr(tool, "name", "Unknown")
                            tool_desc = getattr(tool, "description", "No description")
                            # 格式化工具参数Schema为JSON字符串
                            tool_params = json.dumps(
                                tool.inputSchema, indent=2, ensure_ascii=False
                            )

                            # 拼接工具信息到content变量
                            content += f"工具 {index}: {tool_name}\n"
                            content += f"描述: {tool_desc}\n"
                            content += f"参数:\n{tool_params}\n\n"

                            # 使用Rich Panel显示单个工具的详细信息
                            console.print(
                                Panel(
                                    f"[bold cyan]工具 {index}: {tool_name}[/bold cyan]\n"
                                    f"[yellow]描述:[/yellow] {tool_desc}\n"
                                    f"[yellow]参数:[/yellow]\n{tool_params}",
                                    title=f"工具详情",
                                    border_style="blue",
                                )
                            )
                        # 将工具列表信息添加到聊天历史，供后续对话参考
                        payload.append({"role": "assistant", "content": content})

                    except Exception as e:
                        # 处理获取工具列表时的错误
                        error_msg = f"获取工具列表失败: {str(e)}"
                        console.print(
                            Panel(
                                f"[red]{error_msg}[/red]",
                                title="错误",
                                border_style="red",
                            )
                        )
                        # 将错误信息添加到聊天历史
                        payload.append({"role": "assistant", "content": error_msg})

                elif command["action"] == "call_tool":
                    # 调用指定的工具
                    tool_name = command["tool_name"]
                    parameters = command["parameters"]
                    result = await call_tool(tool_name, parameters)
                    # 处理工具调用结果
                    if isinstance(result, str) and result.startswith("调用工具失败"):
                        # 显示调用失败信息
                        console.print(
                            Panel(
                                f"[red]{result}[/red]",
                                title="错误",
                                border_style="red",
                            )
                        )
                        # 将错误信息添加到聊天历史
                        payload.append({"role": "assistant", "content": result})
                    else:
                        # 显示调用成功信息
                        console.print(
                            Panel(
                                f"[green]工具调用成功，结果: {result}[/green]",
                                title="工具调用结果",
                                border_style="green",
                            )
                        )
                        # 将成功结果添加到聊天历史
                        payload.append({"role": "assistant", "content": str(result)})
                        # 添加一个后续提示，让LLM总结工具调用结果
                        payload.append(
                            {
                                "role": "user",
                                "content": "工具调用结果如何？请给出简要总结,使用直接回复模板回复。",
                            }
                        )
                        rejudge = True # 设置标志，让LLM在下一轮处理这个总结请求

                elif command["action"] == "direct_reply":
                    # 直接显示LLM的回复内容
                    # 使用Rich Markdown格式化输出
                    md = Markdown(command["content"])
                    console.print(Panel(md, title="回复", border_style="blue"))
                    # 注意：直接回复的内容已在上面添加到payload

            except json.JSONDecodeError:
                # 处理JSON解析失败的情况
                console.print(f"[red]无法解析结果:[/red]\n {reply}")
                # 向LLM发送系统消息，要求其修正输出格式
                payload.append(
                    {
                        "role": "system",
                        "content": "接下来请提供符合格式的回复,即使用JSON,并且避免任何markdown标记。",
                    }
                )
                rejudge = True # 设置标志，让LLM重新生成响应
                rejudge_count += 1 # 增加重试计数
                # 如果重试次数过多，则退出程序
                if rejudge_count > 3:
                    console.print(f"[red] [!] 无法解析结果次数过多，程序退出![/red]")
                    break

        except KeyboardInterrupt:
            # 处理用户按 Ctrl+C 的情况
            console.print("\n[yellow]使用 /quit 退出程序[/yellow]")
            continue # 继续下一次循环，等待用户输入
        except Exception as error:
            # 处理其他未预料的异常
            console.print(f"[red]发生错误:[/red] {str(error)}")
            continue # 继续下一次循环

if __name__ == "__main__":
    # 运行主异步函数
    asyncio.run(main())
