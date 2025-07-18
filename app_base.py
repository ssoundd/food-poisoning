import streamlit as st
import uuid
from main import update_sitotoxism, load_sitotoxism_chroma, prepare_weather_data, prepare_predict_data, create_chain, get_answer
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import AIMessage, HumanMessage

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

session_id = st.session_state.session_id

if "sitotoxism_vs" not in st.session_state:
    update_sitotoxism()
    st.session_state.sitotoxism_vs = load_sitotoxism_chroma()

if "chain" not in st.session_state:
    st.session_state.chain = create_chain()

if "all_memory" not in st.session_state:
    st.session_state.all_memory = {}

if session_id not in st.session_state.all_memory:
    st.session_state.all_memory[session_id] = ConversationBufferMemory(return_messages = True)

user_memory = st.session_state.all_memory[session_id]

st.title("식중독 위험 예측 전문가")

for message in user_memory.chat_memory.messages:

    if isinstance(message, HumanMessage):
        with st.chat_message('user'):
            st.write(message.content)

    elif isinstance(message, AIMessage):
        with st.chat_message('assistant'):
            st.write(message.content)

if user_input := st.chat_input("위치와 함께 질문을 입력하세요."):

    with st.chat_message('user'):
        st.write(user_input)

    user_memory.chat_memory.add_user_message(user_input)

    history = user_memory.load_memory_variables({})['history']

    weather_text = prepare_weather_data(user_input)
    predict_df = prepare_predict_data()

    with st.chat_message('assistant'):

        collect_chunk = []

        def stream_and_collect():
            for chunk in get_answer(st.session_state.sitotoxism_vs, user_input, st.session_state.chain, weather_text, predict_df, history):
                collect_chunk.append(chunk)
                yield chunk

        st.write_stream(stream_and_collect())

    response = ''.join(collect_chunk)

    user_memory.chat_memory.add_ai_message(response)