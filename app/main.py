from typing import TypedDict, Annotated
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage, HumanMessage
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
import asyncio

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
llm = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct")

message_history = []


async def main():
    try:

        server_params = StdioServerParameters(
            command="python",
            args=["@cocal/google-calendar-mcp"],
            env={
                "GOOGLE_OAUTH_CREDENTIALS": r"D:\Github\gmeet-ai-agent\app/credentials.json"
            },
            # Make sure to update to the full absolute path to your math_server.py file
            # args=[r"D:\Github\gmeet-ai-agent\app\google_calendar_server.py"],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the connection
                await session.initialize()

                # Get tools
                tools = await load_mcp_tools(session)

                # Create and run the agent
                agent = create_react_agent(llm, tools)
                print("🗓️ Google Calendar Agent (type 'exit' to quit)\n")
                while True:
                    user_input = input("🧑 You: ")
                    if user_input.lower() in ["exit", "quit"]:
                        break

                    # Add Human message to the message history
                    message_history.append(HumanMessage(content=user_input))
                    print("Inptu...", user_input)
                    agent_response = await agent.ainvoke(
                        {"messages": "GET ME MY EVENTS"}
                    )
                    # message_history.append(AIMessage(content=agent_response))
                    print("🤖 Agent: " + agent_response + "\n")

                await session.shutdown()

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        print("Traceback:", traceback.print_exc())


if __name__ == "__main__":
    asyncio.run(main())
