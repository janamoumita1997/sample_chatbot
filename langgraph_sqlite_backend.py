from langgraph.graph import StateGraph,START,END
from typing import TypedDict,Annotated
from pydantic import BaseModel,Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3


class chatstate(TypedDict):
    messages: Annotated[list[BaseMessage],add_messages]

chatmodel = ChatOllama(model = "llama3.2:1b")
def chat_node(state:chatstate):
    query = state["messages"]
    prompt = ""
    res = chatmodel.invoke(query)
    return {"messages":[res]}


graph = StateGraph(chatstate)
graph.add_node("chat_node",chat_node)

graph.add_edge(START,"chat_node")
graph.add_edge("chat_node",END)

conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)
chatbot = graph.compile(checkpointer=checkpointer)

def get_existing_thread():
    all_thread = set()
    for checkpoint in checkpointer.list(None):
        all_thread.add(checkpoint.config['configurable']['thread_id'])
    return list(all_thread)

# config = {"configurable":{"thread_id":"1"}}
# initial_state = {
#         "messages":[HumanMessage(content="hello, My name is Moumita Jana")]
#     }
# res = chatbot.invoke( initial_state,config=config)
# ai_message = res['messages'][-1].content 
# print(ai_message)

# # for streaming the output:

# for message_chunk,metadata in chatbot.stream(initial_state,config=config,stream_mode="messages"):
#     if message_chunk.content:
#         print(message_chunk.content,end=" ",flush = True)

