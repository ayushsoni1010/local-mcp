import argparse
import asyncio
from ollama_client import get_agent, handle_user_message
from llama_index.core.agent.workflow import Context

async def run_chat(server_url: str):
    """
    Initializes the agent and enters an interactive chat loop.
    """
    # Instantiate agent and context
    agent = await get_agent()
    agent_ctx = Context()
    print("Connected to MCP Agent at {}".format(server_url))
    print("Type 'exit' or 'quit' to end the session.\n")

    while True:
        user_input = input("You: ")
        if user_input.strip().lower() in ('exit', 'quit'):
            print("Session ended. Goodbye!")
            break
        # Send message and await response
        response = await handle_user_message(user_input, agent, agent_ctx)
        print(f"Agent: {response}\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CLI for interacting with the MCP agent')
    parser.add_argument(
        '--server_url',
        type=str,
        default='http://localhost:5000',
        help='Base URL of the MCP server (not used directly here)'
    )
    args = parser.parse_args()
    try:
        asyncio.run(run_chat(args.server_url))
    except KeyboardInterrupt:
        print("\nInterrupted by user. Goodbye!")
