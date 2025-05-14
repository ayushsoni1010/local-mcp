import asyncio
import argparse

from llama_index.llms.ollama import Ollama
from llama_index.core import Settings
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
from llama_index.core.agent.workflow import (
    FunctionAgent,
    ToolCall,
    ToolCallResult,
    Context
)

# Configure LLM
llm = Ollama(model="deepseek-r1", request_timeout=120.0)
Settings.llm = llm

# System prompt guiding the agent
SYSTEM_PROMPT = """
You are an AI assistant that uses available tools to interact with a local SQLite database via MCP.
Always choose the appropriate tool before answering user queries.
"""


async def get_agent() -> FunctionAgent:
    """
    Instantiate and return a FunctionAgent with MCP tools fetched from the local server.
    """
    # Initialize MCP client pointing to our MCP server
    mcp_client = BasicMCPClient(base_url="http://localhost:5000")
    # Discover tools via MCP
    tool_spec = McpToolSpec(client=mcp_client)
    tools = await tool_spec.to_tool_list_async()

    # Build agent with discovered tools
    agent = FunctionAgent(
        name="MCPAgent",
        description="Agent that selects and calls MCP tools based on user queries.",
        system_prompt=SYSTEM_PROMPT,
        verbose=True,
        tools=tools,
        llm=llm
    )
    return agent

async def handle_user_message(
    message: str,
    agent: FunctionAgent,
    agent_ctx: Context,
    verbose: bool = True
) -> str:
    """
    Send user message to agent, stream tool calls & results, and return final response.
    """
    handler = agent.run(message, context=agent_ctx)
    async for event in handler.stream_events():
        if verbose and isinstance(event, ToolCall):
            print(f"Calling tool: {event.tool_name} with args: {event.tool_kwargs}")
        elif verbose and isinstance(event, ToolCallResult):
            print(f"Tool result ({event.tool_name}): {event.tool_call_output}")

    response = await handler
    return str(response)

async def main(server_url: str):
    """
    Entrypoint for interactive CLI chat with the MCP agent.
    """
    print("Initializing agent and context...")
    agent = await get_agent()
    context = Context()
    print("Agent ready. Type 'exit' to quit.")

    while True:
        user_input = input("You: ")
        if user_input.strip().lower() == 'exit':
            print("Goodbye!")
            break
        reply = await handle_user_message(user_input, agent, context)
        print(f"Agent: {reply}\n")
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the Ollama MCP client')
    parser.add_argument(
        '--server_url',
        type=str,
        default='http://localhost:5000',
        help='Base URL of the MCP server'
    )
    args = parser.parse_args()
    try:
        asyncio.run(main(args.server_url))
    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting.")