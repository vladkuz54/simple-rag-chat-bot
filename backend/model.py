import numpy as np
import psycopg2

from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, get_embedding, ollama_client, MODEL_NAME


conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)
cursor = conn.cursor()


def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def get_top_k_chunks(question, table_name, k=3):
    q_emb = get_embedding(question)
    cursor.execute(f'SELECT id, content, embedding FROM {table_name}')
    rows = cursor.fetchall()
    scored = []
    for row in rows:
        emb = [float(x) for x in row[2].strip('[]').split(',')]
        sim = cosine_similarity(q_emb, emb)
        scored.append((sim, row[1]))
    scored.sort(reverse=True, key=lambda x: x[0])
    return [text for _, text in scored[:k]]


def answer_question(question, table_name):
    top_chunks = get_top_k_chunks(question, table_name, k=10)
    context = '\n---\n'.join(top_chunks)
    prompt = f"Answer the question using the context below.\nContext:\n{context}\nQuestion: {question}\nAnswer:"
    response = ollama_client.generate(model=MODEL_NAME, prompt=prompt)
    answer = response['response'] if 'response' in response else response.get('text', '')
    print(f"The question: {question}\nThe answer: {answer}\n")

