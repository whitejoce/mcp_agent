#!/usr/bin/env python3
# -*- coding=utf-8 -*-

#from: https://gofastmcp.com/getting-started/welcome
from fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Demo", debug=True, log_level="DEBUG")

# Add an addition tool
@mcp.tool()
def add(a: int,b: int)-> int:
    """Add two numbers"""
    return a+b

if __name__ =="__main__":
    mcp.run(transport="sse")