from ollama import Client

DB_HOST = 'localhost'
DB_PORT = 5432
DB_NAME = 'rag'
DB_USER = 'postgres'
DB_PASSWORD = '2006vkuz'

DATA_DIR = 'data'

ollama_client = Client()
MODEL_NAME = 'mistral:7b-instruct-q4_K_M'
EMBEDDING_SIZE = 4096


def get_embedding(text):
    response = ollama_client.embeddings(model=MODEL_NAME, prompt=text)
    return response['embedding']
