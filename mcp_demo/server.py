#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Coder:Whitejoce

from fastmcp import FastMCP
import subprocess

# Create an MCP server
mcp = FastMCP("Demo", debug=True, log_level="DEBUG")

@mcp.tool()
def add(a: int,b: int)-> int:
    """Add two numbers"""
    return a+b

def decode_output(output_bytes):
    """Attempts to decode byte string using common encodings."""
    encodings = ['utf-8', 'gbk', 'cp936']  # Common encodings, especially for Windows
    for enc in encodings:
        try:
            return output_bytes.decode(enc)
        except UnicodeDecodeError:
            #print(f"Decoding with {enc} failed, trying next encoding...")
            continue
    # Fallback if none of the preferred encodings work
    return output_bytes.decode('utf-8', errors='replace')

@mcp.tool()
def execute_command(command: str) -> tuple[bool, str]:
    """Execute a shell command and return the output."""
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            # text=True, # Capture raw bytes instead of text
            # errors='replace', # Error handling will be done during decoding
        )
        stdout_bytes, stderr_bytes = process.communicate()
        stdout = decode_output(stdout_bytes)
        stderr = decode_output(stderr_bytes)

        if process.returncode == 0:
            return True, stdout
        else:
            error_output = stderr if stderr.strip() else stdout
            return False, error_output.strip()
    except Exception as e:
        return False, str(e)


if __name__ =="__main__":
    mcp.run(transport="sse")