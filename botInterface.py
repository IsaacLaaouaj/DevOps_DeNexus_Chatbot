import streamlit as st
import random
import time
from RAG import ChatBot
from pymongo import MongoClient
import pickle
import base64
import os
import logging
import sys
from kafka import KafkaProducer
import json
import uuid

# Configurar logging a stdout
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

# Ejemplo de uso
logger.info("Chatbot iniciado")
logger.warning("Esto es un warning")
logger.error("Esto es un error")


chat = ChatBot()

def response_generator(userInput,botContext):
    response = chat.llamaResponse(userInput)
    for word in response.split():
        yield word + " "
        time.sleep(0.05)

st.title("Chat DeNexus")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What do you want to ask?",key=2):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = st.write_stream(response_generator(prompt, ""))
    st.session_state.messages.append({"role": "assistant", "content": response})


producer = KafkaProducer(
    bootstrap_servers='localhost:9092',  # usar 'kafka:9092' si está dentro del contenedor
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

session_id = st.session_state.get("session_id", str(uuid.uuid4()))
st.session_state.session_id = session_id

if prompt := st.chat_input("¿Qué quieres preguntar?"):
    message = {"session_id": session_id, "message": prompt}
    producer.send("chat-messages", message)
    producer.flush()
    st.markdown("✅ Tu mensaje ha sido enviado al chatbot. Espera una respuesta.")
