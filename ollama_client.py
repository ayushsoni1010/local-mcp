import asyncio
import logging
import sqlite3
import argparse
from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
from llama_index.core.workflow import Context
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
from llama_index.core.agent.workflow import (
    ToolCall,
    ToolCallResult,
    FunctionAgent,
)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize the SQLite DB
def init_db():
    """Initialize the SQLite database"""
    connection = sqlite3.connect('demo.db')
    cursor = connection.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS people(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        profession TEXT NOT NULL
    )
    ''')
    connection.commit()
    connection.close()
    logger.info("Database initialized")

# Initialize the LLM
llm = None

# System prompt to guide the agent's behavior
SYSTEM_PROMPT = """
You are an AI assistant for Tool Calling.
Before helping, work with our tools to interact with our database.
Always use the most appropriate tool based on the user's request.
For database queries:
- Use read_data to fetch information
- Use add_data to insert new records
Respond with clear and concise information derived from the database.
"""

async def get_agent(tools: McpToolSpec):
    """
    Creates and returns a FunctionAgent with the provided tools.
    
    Args:
        tools (McpToolSpec): MCP tools specification
        
    Returns:
        FunctionAgent: Configured agent with tools
    """
    tool_list = await tools.to_tool_list_async()
    for tool in tool_list:
        logger.info(f"Tool: {tool.metadata.name}, Description: {tool.metadata.description}")
    
    agent = FunctionAgent(
        name="DatabaseAgent",
        description="Agent that can call tools and interact with the database.",
        system_prompt=SYSTEM_PROMPT,
        verbose=True,
        tools=tool_list,
        llm=llm,
    )
    
    return agent

async def handle_user_message(
    message: str,
    agent: FunctionAgent,
    agent_context: Context,
    verbose: bool = False
):
    """
    Process user message with the agent and return response.
    
    Args:
        message (str): User input message
        agent (FunctionAgent): The function agent
        agent_context (Context): Agent context for maintaining history
        verbose (bool): Whether to print verbose output
        
    Returns:
        str: Agent's response
    """
    logger.info(f"Processing user message: {message}")
    
    handler = agent.run(message, ctx=agent_context)
    
    async for event in handler.stream_events():
        if verbose and type(event) == ToolCall:
            logger.info(f"Calling Tool: {event.tool_name} with kwargs: {event.tool_kwargs}")
        elif verbose and type(event)== ToolCallResult: 
            logger.info(f"Tool Result: {event.tool_name} returned {event.content}")
    
    response = await handler
    return str(response)

async def main():
    """
    Main function to run the MCP client.
    """
    
    parser = argparse.ArgumentParser(description="MCP Agent for database operations")
    parser.add_argument("--mcp-url", type=str, default="http://0.0.0.0:8000/sse", 
                        help="URL for MCP server (default: http://0.0.0.0:8000/sse)")
    parser.add_argument("--model", type=str, default="llama3", 
                        help="Ollama model to use (default: llama3)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    # Initialize the LLM with the specified model
    global llm
    llm = Ollama(model=args.model, request_timeout=120.0)
    Settings.llm = llm

    logger.info(f"Using Ollama model: {args.model}")
    
    # Connect to MCP server
    logger.info(f"Connecting to MCP server at {args.mcp_url}...")
    mcp_client = BasicMCPClient(args.mcp_url)
    tools_spec = McpToolSpec(client=mcp_client)
    
    # Initialize agent
    logger.info("Initializing agent...")
    agent = await get_agent(tools_spec)
    agent_context = Context(agent)
    
    # Interactive chat loop
    logger.info("Starting chat session. Type 'exit' to quit.")
    print("\n<<<====== MCP Agent Chat Session ======>>>")
    print("Type 'exit', 'quit', or 'bye' to quit the session")
    
    while True:
        user_input = input("\nEnter your message: ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Goodbye!")
            break
            
        print("\nProcessing...")
        try:
            response = await handle_user_message(user_input, agent, agent_context)
            print(f"\nAgent: {response}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    # Initialize the database
    init_db()
    asyncio.run(main())