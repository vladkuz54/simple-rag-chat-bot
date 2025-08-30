import os
import psycopg2
from langchain.text_splitter import RecursiveCharacterTextSplitter


def filling_database(DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, DATA_DIR, get_embedding):
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=500,
        length_function=len,
        is_separator_regex=False,
    )

    for filename in os.listdir(DATA_DIR):
        print(f'Processing file: {filename}')
        file_path = os.path.join(DATA_DIR, filename)
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                chunks = text_splitter.split_text(content)
                for chunk in chunks:
                    print(f'Processing chunk of size {len(chunk)}')
                    embedding = get_embedding(chunk)
                    embedding_str = '[' + ','.join(str(x) for x in embedding) + ']'
                    cursor.execute(
                        """
                        INSERT INTO items (content, embedding)
                        VALUES (%s, %s)
                        """,
                        (chunk, embedding_str)
                    )
                print(f'Inserted {len(chunks)} chunks from {filename}')

    conn.commit()
    cursor.close()
    conn.close()
