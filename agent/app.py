import asyncio
import json
import os

from mcp import Resource
from mcp.types import Prompt

from agent.dial_client import DialClient
from agent.mcp_client import MCPClient
from agent.models.message import Message
from agent.models.message import Role
from agent.prompts import SYSTEM_PROMPT

# https://remote.mcpservers.org/fetch/mcp
# Pay attention that `fetch` doesn't have resources and prompts


async def main():
    # TODO:
    # 1. Create MCP client and open connection to the MCP server (use `async with {YOUR_MCP_CLIENT} as mcp_client`),
    #    mcp_server_url="http://localhost:8005/mcp"
    # 2. Get Available MCP Resources and print them
    # 3. Get Available MCP Tools, assign to `tools` variable, print tool as well
    # 4. Create DialClient
    # 5. Create list with messages and add there SYSTEM_PROMPT with instructions to LLM
    # 6. Add to messages Prompts from MCP server as User messages
    # 7. Create console chat (infinite loop + ability to exit from chat + preserve message history after the call to dial client)
    mcp_server_url = "http://localhost:8005/mcp"
    async with MCPClient(mcp_server_url=mcp_server_url) as mcp_client:
        resources = await mcp_client.get_resources()
        print("Available MCP Resources:")
        for resource in resources:
            print(f"- {resource.name} ({resource.description})")

        tools = await mcp_client.get_tools()
        print("\nAvailable MCP Tools:")
        for tool in tools:
            print(f"- {tool['function']['name']} ({tool['function']['description']})")

        dial_client = DialClient(
            api_key=os.getenv("DIAL_API_KEY", ""),
            endpoint="https://ai-proxy.lab.epam.com",
            mcp_client=mcp_client,
            tools=tools,
        )

        messages = [Message(role=Role.SYSTEM, content=SYSTEM_PROMPT)]

        prompts = await mcp_client.get_prompts()
        for prompt in prompts:
            content = await mcp_client.get_prompt(prompt.name)
            messages.append(
                Message(
                    role=Role.USER,
                    content=f"## Prompt provided by MCP server:\n{prompt.description}\n{content}",
                )
            )

        print("\nStarting console chat. Type 'exit' to quit.")
        while True:
            user_input = input("You: ")
            if user_input.lower() == "exit":
                break

            messages.append(Message(role=Role.USER, content=user_input))

            ai_message = await dial_client.get_completion(messages)
            messages.append(ai_message)


if __name__ == "__main__":
    asyncio.run(main())
