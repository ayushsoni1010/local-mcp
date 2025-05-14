from llama_index.agent import FunctionCallingAgent
from llama_index.llms import Ollama
from llama_index.tools.mcp import MCPToolSpec
from llama_index.tools.mcp.base import BasicMCPClient

llm = Ollama(model="deepseek-r1")

mcp_client = BasicMCPClient(base_url="http://localhost:5000")

tool_spec = MCPToolSpec(client=mcp_client)
tools = tool_spec.to_tool_list()

with open('system_prompt.txt', 'r') as f:
    system_prompt = f.read()
    
agent = FunctionCallingAgent.from_tools(
    tools=tools,
    system_prompt=system_prompt,
    llm=llm,
)