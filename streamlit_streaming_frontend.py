import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage


if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

for message in st.session_state['message_history']:
    with st.chat_message(message["role"]):
        st.text(message['content'])

user_input = st.chat_input("Type here")

if user_input:
    st.session_state['message_history'].append({"role":"user","content":user_input})
    with st.chat_message("user"):
        st.text(user_input)

    config = {"configurable":{"thread_id":"1"}}
    initial_state = {
        "messages":[HumanMessage(content=f"{user_input}")]
    }

    # res = chatbot.invoke(initial_state,config=config)
    # ai_message = res['messages'][-1].content 

    # st.session_state['message_history'].append({"role":"assistance","content":ai_message})
    with st.chat_message('assistant'):
        # st.text(ai_message)
        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(initial_state,config= config,stream_mode="messages")
        )
    st.session_state['message_history'].append({"role":"assistance","content":ai_message})
