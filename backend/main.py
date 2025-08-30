import os
import psycopg2
from flask import Flask, request, jsonify
import pdfplumber
from docx import Document


from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, DATA_DIR, get_embedding
from model import answer_question
from filling_database import filling_database

app = Flask(__name__, static_folder='../app/build', static_url_path='/')


conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)
cursor = conn.cursor()

def is_db_empty():
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'items'
        )
    """)
    table_exists = cursor.fetchone()[0]
    if not table_exists:
        print("Table 'items' does not exist.")
        print('Creating table...')
        cursor.execute("""
            create extension if not exists vector;

            create table items (
	            id serial primary key,
	            content text,
	            embedding vector(4096)
            );
        """)
        conn.commit()
        return True
    cursor.execute('SELECT COUNT(*) FROM items')
    count = cursor.fetchone()[0]
    return count == 0

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    question = data.get('question', '')
    if not question:
        return jsonify({'error': 'No question provided'}), 400
    from model import answer_question
    import io
    import sys
    old_stdout = sys.stdout
    sys.stdout = mystdout = io.StringIO()
    answer_question(question)
    sys.stdout = old_stdout
    output = mystdout.getvalue()
    answer = output.split('The answer:')[-1].strip() if 'The answer:' in output else output.strip()
    return jsonify({'question': question, 'answer': answer})

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    for f in os.listdir(DATA_DIR):
        os.remove(os.path.join(DATA_DIR, f))

    cursor.execute('DELETE FROM items')
    conn.commit()

    ext = os.path.splitext(file.filename)[1].lower()
    base_filename = os.path.splitext(file.filename)[0]
    save_path = os.path.join(DATA_DIR, base_filename + '.md')

    if ext == '.pdf':
        with pdfplumber.open(file) as pdf:
            text = '\n'.join(page.extract_text() or '' for page in pdf.pages)
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(text)
    elif ext in ['.docx', '.doc']:
        doc = Document(file)
        text = '\n'.join([para.text for para in doc.paragraphs])
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(text)
    elif ext == '.md' or ext == '.txt':
        file.save(os.path.join(DATA_DIR, base_filename + ext))
    else:
        return jsonify({'error': 'Unsupported file type'}), 400

    filling_database(DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, DATA_DIR, get_embedding)

    return jsonify({'message': 'File uploaded and database updated.', 'filename': base_filename})

@app.route('/status', methods=['GET'])
def status():
    files = [f for f in os.listdir(DATA_DIR) if os.path.isfile(os.path.join(DATA_DIR, f))]
    filename = files[0] if files else None
    cursor.execute('SELECT COUNT(*) FROM items')
    count = cursor.fetchone()[0]
    db_filled = count > 0
    return jsonify({'db_filled': db_filled, 'filename': filename})

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    return app.send_static_file('index.html')

if __name__ == '__main__':
    if is_db_empty():
        if not os.path.exists(DATA_DIR) or not os.listdir(DATA_DIR):
            print(f"Directory '{DATA_DIR}' is empty. Please add files to proceed.")
        else:
            filling_database(DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, DATA_DIR, get_embedding)
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    app.run(host='localhost', port=5000)
