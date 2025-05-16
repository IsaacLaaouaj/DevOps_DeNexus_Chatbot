import os
import pandas as pd
from groq import Groq
from uuid import uuid4
from tqdm import tqdm
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter


class ChatBot():

    def __init__(self):
        self.k = 5
        self.documents = []
        self.model_name = 'sentence-transformers/all-mpnet-base-v2'
        self.carga_documentos()
        self.search_with_langchain_faiss()

    def carga_documentos(self):
        # Cargar solo HACKMAGEDDON
        titulo_documento = 'HACKMAGEDDON'
        columns = ['Description']
        df = pd.read_csv(f'data/{titulo_documento}_cleaned.csv')
        df = df[columns]
        df['id'] = df.index

        for _, r in df.iterrows():
            self.documents.append(
                Document(
                    page_content=r.iloc[0],  # Usamos iloc para evitar FutureWarning
                    metadata={
                        "source": titulo_documento,
                        "id": r['id']
                    }
                )
            )

    def search_with_langchain_faiss(self):
        embeddings = HuggingFaceEmbeddings(model_name=self.model_name)

        try:
            print('Cargando base de datos')
            self.faiss_index = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        except:
            print('Base de datos no encontrada, generamos base de datos')
            print("Generando índice FAISS...")
            with tqdm(total=len(self.documents), desc="Procesando documentos") as pbar:
                self.faiss_index = FAISS.from_documents(
                    self.documents,
                    embedding=embeddings,
                    progress_callback=lambda: pbar.update(1)
                )
            self.faiss_index.save_local("faiss_index")
            print("Índice FAISS generado y guardado.")

    def busca_contexto(self, query):
        results = self.faiss_index.similarity_search(query, k=self.k)
        return [result.page_content for result in results]

    def llamaResponse(self, query):
        client = Groq(
            api_key='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',
        )

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"""
                    You are an assistant designed to answer questions related to cybersecurity.
                    Please, only answer the question with the context provided. If the context
                    does not provide the answer to the user's question, just say 'I don't know'.
                    The context is: {self.busca_contexto(query)}
                    """
                },
                {
                    "role": "user",
                    "content": query,
                }
            ],
            model="llama-3.3-70b-versatile",
        )

        return chat_completion.choices[0].message.content
