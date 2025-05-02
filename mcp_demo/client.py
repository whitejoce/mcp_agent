#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Coder:Whitejoce

from fastmcp import Client
from fastmcp.client.transports import (
    SSETransport
)

import asyncio,json

async def main():
    async with Client(SSETransport("http://127.0.0.1:8000/sse")) as client:
        tools = await client.list_tools()
        print("Available tools:")
        print(f"Total tools: {len(tools)}")
        for _ , tool in enumerate(tools):
            print("------------------------------------")
            print(f"- tool [{getattr(tool, 'name', 'Unknown')}], \ndescription: {getattr(tool, 'description', 'No description')}, \nparameters: {json.dumps(tool.inputSchema,indent=2)}")
        #result = await client.call_tool("add", {'a': 5, 'b': 3})
        #print("Result of add(5, 3):", result)

if __name__ == "__main__":
    asyncio.run(main())