# Create server parameters for stdio connection
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
import asyncio
import os


os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGSMITH_TRACING_V2", "true")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGSMITH_PROJECT")

llm = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct")


async def main():

    server_params = StdioServerParameters(
        command="npx",
        # Make sure to update to the full absolute path to your math_server.py file
        # args=["/path/to/math_server.py"],
        # args=[r"D:\Github\gmeet-ai-agent\app\math\math_server.py"],
        args=["@cocal/google-calendar-mcp"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            # Get tools
            tools = await load_mcp_tools(session)

            # Create and run the agent
            agent = create_react_agent(llm, tools)
            agent_response = await agent.ainvoke({"messages": "what's (3 + 5) x 12?"})
            print("agent response:", agent_response)


if __name__ == "__main__":
    asyncio.run(main())
