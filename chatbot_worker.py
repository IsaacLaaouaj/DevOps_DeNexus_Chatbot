from kafka import KafkaConsumer
import json
from RAG import ChatBot

chat = ChatBot()

consumer = KafkaConsumer(
    'chat-messages',
    bootstrap_servers='kafka:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='chatbot-group'
)

print("👂 Esperando mensajes...")

for msg in consumer:
    user_input = msg.value["message"]
    session_id = msg.value["session_id"]

    print(f"[{session_id}] Mensaje recibido: {user_input}")
    response = chat.llamaResponse(user_input)
    print(f"[{session_id}] Respuesta generada: {response}")

