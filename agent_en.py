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

# API Configuration
API_CONFIG = {
    "url": "",
    "api_key": "",  # your API key here
    "model": "Qwen/Qwen2.5-7B-Instruct",
    "MCP_Server": "http://127.0.0.1:8000/sse"  # MCP server URL
}

# Validate API configuration
assert (
    API_CONFIG["url"] != "your_url" and API_CONFIG["api_key"] != ""
), "Please fill in the correct url and api_key"

# System Prompt
SYSTEM_PROMPT = """
You are an intelligent terminal assistant. You need to select the appropriate operation method based on the user's request. You must strictly output in JSON format, without Markdown.

Rules:
1. When the user's intent can be accomplished using built-in tools, prioritize calling the tool and generate the call command and required parameters.
2. If no operation is needed, just reply directly with the answer.

The JSON format must conform to:
- Show tools example:
{
    "action": "show_tools",
    "explain": "List all available tools"
}
- Call tool example:
{
  "action": "call_tool",
  "tool_name": "list_files",
  "parameters": {
    "path": "/home/user"
  }
}
- Direct reply example:
{
  "action": "direct_reply",
  "content": "This is the content of the direct reply"
}
"""

# Initialize Rich components
console = Console()

# Initialize OpenAI client
client = OpenAI(api_key=API_CONFIG["api_key"], base_url=API_CONFIG["url"])

payload = [{"role": "system", "content": SYSTEM_PROMPT}]


def get_chat_response(client, payload):
    response = client.chat.completions.create(
        model=API_CONFIG["model"], messages=payload, stream=True
    )
    reply_chunk, reasoning_chunk = [], []
    full_reply = ""
    has_reasoning = False
    with console.status("[bold green]Thinking...[/bold green]") as status:
        for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                reply_chunk.append(content)
                full_reply += content

            # Note:
            # Standard OpenAI API does not have 'reasoning_content' in the delta.
            # If this causes an error, you might need to adjust or remove this part.
            if hasattr(chunk.choices[0].delta, 'reasoning_content') and chunk.choices[0].delta.reasoning_content:
                has_reasoning = True
                reasoning_content = chunk.choices[0].delta.reasoning_content
                reasoning_chunk.append(reasoning_content)
                status.stop()
                console.print(reasoning_content, end="")

    if has_reasoning:
        print()
    #print("".join(reply_chunk))
    return "".join(reply_chunk), "".join(reasoning_chunk)


def execute_command(cmd):
    # Execute command and preserve color output
    try:
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        stdout, stderr = process.communicate()

        if process.returncode == 0:
            return True, stdout
        else:
            return False, stderr
    except Exception as e:
        return False, str(e)


async def get_tools_list():
    async with Client(SSETransport(API_CONFIG["MCP_Server"])) as client:
        tools = await client.list_tools()
        return tools

async def call_tool(tool_name, parameters):
    async with Client(SSETransport(API_CONFIG["MCP_Server"])) as client:
        try:
            result = await client.call_tool(tool_name, parameters)
            return result
        except Exception as e:
            return f"Failed to call tool: {str(e)}"



async def main():
    rejudge = False
    rejudge_count = 0
    while True:
        try:
            if not rejudge:
                rejudge = False
                user_input = Prompt.ask("[bold blue]Smart_Shell>[/bold blue]")

                if user_input.lower() in ["/quit", "exit", "quit"]:
                    console.print("[yellow]Goodbye![/yellow]")
                    break

                payload.append({"role": "user", "content": user_input})

            reply, reasoning = get_chat_response(client, payload)

            try:
                pattern = re.compile(r"```json\n(.*?)\n```", re.S)
                if pattern.search(reply):
                    reply = pattern.findall(reply)[0]
                command = json.loads(reply)
                payload.append({"role": "assistant", "content": reply})
                rejudge = False
                rejudge_count = 0
                if command["action"] == "show_tools":
                    try:
                        tools = await get_tools_list()
                        content = f"Found {len(tools)} available tools:\n\n"

                        console.print(
                            Panel(
                                f"[bold green]Found {len(tools)} available tools[/bold green]",
                                title="Tool List",
                                border_style="green",
                            )
                        )

                        for index, tool in enumerate(tools, 1):
                            tool_name = getattr(tool, "name", "Unknown")
                            tool_desc = getattr(tool, "description", "No description")
                            tool_params = json.dumps(
                                tool.inputSchema, indent=2, ensure_ascii=False
                            )

                            content += f"Tool {index}: {tool_name}\n"
                            content += f"Description: {tool_desc}\n"
                            content += f"Parameters:\n{tool_params}\n\n"

                            console.print(
                                Panel(
                                    f"[bold cyan]Tool {index}: {tool_name}[/bold cyan]\n"
                                    f"[yellow]Description:[/yellow] {tool_desc}\n"
                                    f"[yellow]Parameters:[/yellow]\n{tool_params}",
                                    title=f"Tool Details",
                                    border_style="blue",
                                )
                            )

                        payload.append({"role": "assistant", "content": content})

                    except Exception as e:
                        error_msg = f"Failed to get tool list: {str(e)}"
                        console.print(
                            Panel(
                                f"[red]{error_msg}[/red]",
                                title="Error",
                                border_style="red",
                            )
                        )
                        payload.append({"role": "assistant", "content": error_msg})
                elif command["action"] == "call_tool":
                    tool_name = command["tool_name"]
                    parameters = command["parameters"]
                    result = await call_tool(tool_name, parameters)
                    if isinstance(result, str) and result.startswith("Failed to call tool:"):
                        console.print(
                            Panel(
                                f"[red]{result}[/red]",
                                title="Error",
                                border_style="red",
                            )
                        )
                        payload.append({"role": "assistant", "content": result}) # Log error
                    else:
                        console.print(
                            Panel(
                                f"[green]Tool called successfully, result: {result}[/green]",
                                title="Tool Call Result",
                                border_style="green",
                            )
                        )
                        # Send result back to LLM for summarization/next step
                        payload.append({"role": "tool", "tool_call_id": "N/A", "name": tool_name, "content": str(result)}) # Use tool role if possible
                        payload.append(
                            {
                                "role": "user",
                                "content": "The tool call was successful. Please summarize the result using the direct reply template.",
                            }
                        )
                        rejudge = True # Ask LLM to process the tool result

                elif command["action"] == "direct_reply":
                    # Direct reply formatted with Markdown
                    md = Markdown(command["content"])
                    console.print(Panel(md, title="Reply", border_style="blue"))
                    # No need to append direct reply back to payload unless you want the LLM to remember its own replies

            except json.JSONDecodeError:
                console.print(f"[red]Could not parse JSON result:[/red]\n {reply}")
                payload.append(
                    {
                        "role": "system",
                        "content": "The previous response was not valid JSON. Please provide a response strictly in the required JSON format, avoiding any markdown tags or other text outside the JSON structure.",
                    }
                )
                rejudge = True
                rejudge_count += 1
                if rejudge_count > 3:
                    console.print(f"[red] [!] Too many JSON parsing errors, exiting program![/red]")
                    break

        except KeyboardInterrupt:
            console.print("\n[yellow]Use /quit to exit the program[/yellow]")
            continue
        except Exception as error:
            console.print(f"[red]An unexpected error occurred:[/red] {str(error)}")
            # Optionally add error details to payload for context, or just continue
            # payload.append({"role": "system", "content": f"An error occurred: {str(error)}"})
            continue


if __name__ == "__main__":
    asyncio.run(main())
