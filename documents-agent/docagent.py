from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain.llms import OpenAI
import os, sys, openai
from dotenv import load_dotenv
from langchain.tools import tool, Tool

@tool
def search_api(question: str) -> str:
    """Searches the relevant information from the document set to answer the question."""
    return ''''''

class DocAgent:
    def __init__(self):
        load_dotenv() 
        api_key = os.getenv("OPENAI_KEY")
        llm = OpenAI(temperature=0, openai_api_key=api_key)
        tools = [search_api]
        tools = tools + load_tools(["llm-math"], llm=llm)
        self.agent_executor = initialize_agent(
            tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True
        )

    def solve(self, question):
        response = self.agent_executor.invoke(
            {
                "input": question
            }
        )
        return response['output']





