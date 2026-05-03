import streamlit as st
from langgraph_sqlite_backend import chatbot,get_existing_thread
from langchain_core.messages import HumanMessage
import uuid

#--------------------------------utility function-----------------------------------
def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread_id(thread_id)
    st.session_state['message_history'] = []

def add_thread_id(thread_id):
    if thread_id not in st.session_state['chat_thread']:
        st.session_state['chat_thread'].append(thread_id)

def load_conversation(thread_id):
    return chatbot.get_state(config = {"configurable":{"thread_id":thread_id}}).values['messages']
#-----------------------------session setup-----------------------------------------
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()
if 'chat_thread' not in st.session_state:
    st.session_state['chat_thread'] = get_existing_thread()

add_thread_id(st.session_state['thread_id'])

#------------------------------add sidebar------------------------------------------
st.sidebar.title("chat with me")
if st.sidebar.button("new_chat"):
    reset_chat()
st.sidebar.header("Conversation")
for thread in st.session_state['chat_thread'][::-1]:
    if st.sidebar.button(str(thread)):
        st.session_state['thread_id'] = thread
        messages = load_conversation(thread)

        template_messages = []
        for message in messages:
            if isinstance(message, HumanMessage):
                role = 'user'
            else:
                role = 'asistance'
            
            template_messages.append({'role':role,'content':message.content})
        st.session_state['message_history'] = template_messages
#-------------------------------load_conversation-------------------------------------
for message in st.session_state['message_history']:
    with st.chat_message(message["role"]):
        st.text(message['content'])
# new chat
user_input = st.chat_input("Type here")

if user_input:
    st.session_state['message_history'].append({"role":"user","content":user_input})
    with st.chat_message("user"):
        st.text(user_input)

    config = {"configurable":{"thread_id":st.session_state['thread_id']}}
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


