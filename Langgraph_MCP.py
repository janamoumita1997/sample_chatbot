# import all libreries
from langgraph.graph import StateGraph,START,END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage,HumanMessage
from langchain_ollama import ChatOllama
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
import sqlite3
import requests
import asyncio

# global checkpointer
checkpointer = None
chatbot = None

# llm
llm = ChatOllama(model='llama3.2:1b')

## define tools
# inbuild tool
search_tool = DuckDuckGoSearchRun(region='en-us')

# custom tool
@tool
def calculator(first_num: float, second_num: float, oparator: str) -> dict:
    """
    Perform a basic arithmatic oparation on two numbers.
    Supported oparation: add, sub, mul, div
    """
    try:
        if oparator == 'add':
            result = first_num + second_num
        elif oparator == 'sub':
            result = first_num - second_num
        elif oparator == 'mul':
            result = first_num * second_num
        elif oparator == 'div':
            if second_num == 0:
                return {'error':'Division by zero is not allowed'}
            result = first_num / second_num
        else:
            return {'error': f'Unsupported oparator {oparator}'}
        return {'first_num':first_num, 'second_num':second_num, 'oparator':oparator, 'result': result}
    except Exception as e:
        return {'error': str(e)}


@tool
def get_stock_price(symbol:str) -> dict:
    """
    Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') 
    using Alpha Vantage with API key in the URL.
    """
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=C9PE94QUEW9VWGFM"
    r = requests.get(url)
    return r.json()

tools = [search_tool, calculator, get_stock_price]
llm_with_tools = llm.bind_tools(tools)


## define langgraph
# state
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

async def build_graph():
    ## define Nodes
    async def chatNode(state: ChatState):
        """
        LLM call that may answer or request a tool call
        """
        messages = state['messages']
        response = await llm_with_tools.ainvoke(messages)
        return {'messages':[response]}

    tool_node = ToolNode(tools)

    # ## define checkpointer
    # conn = sqlite3.connect(database = 'chatbot.db', check_same_thread = False)
    # checkpointer = SqliteSaver(conn = conn)
    # checkpointer = AsyncSqliteSaver.from_conn_string("chatbot.db")
    graph = StateGraph(ChatState)
    graph.add_node('chatnode',chatNode)
    graph.add_node('tools',tool_node)

    graph.add_edge(START,"chatnode")
    graph.add_conditional_edges("chatnode",tools_condition)
    graph.add_edge('tools','chatnode')

    chatbot = graph.compile()
    return chatbot
async def main():
    config = {'configurable': {'thread_id':'1'}}
    chatbot = await build_graph()
    initial_state = {'messages': [HumanMessage(content = "what is the stock price of Apple")]}

    res = await chatbot.ainvoke(initial_state, config = config)

    print(res['messages'][-1].content)

if __name__ == '__main__':
    asyncio.run(main())
