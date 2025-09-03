
# simple-rag-chat-bot

## Project Setup Instructions

Follow these steps to set up and run the project:

---

### Creating a PostgreSQL Database

1. **Install PostgreSQL**  
	Download and install PostgreSQL from the official website: https://www.postgresql.org/download/

2. **Create a new database**  
	Open the PostgreSQL shell (psql) and run:
	```sql
	CREATE DATABASE ragdb;
	CREATE USER raguser WITH ENCRYPTED PASSWORD 'yourpassword';
	GRANT ALL PRIVILEGES ON DATABASE ragdb TO raguser;
	```

3. **Update your project configuration**  
	Edit `backend/config.py` and set your database connection details:
	```python
	DB_HOST = 'localhost'
	DB_PORT = 5432
	DB_NAME = 'ragdb'
	DB_USER = 'raguser'
	DB_PASSWORD = 'yourpassword'
	```

---

1. **Clone the repository**  
	Download the project files to your local machine using Git:
	```powershell
	git clone <repository-url>
	```

2. **Install Python dependencies**  
	Navigate to the `backend` directory and install required packages:
	```powershell
	cd backend
	pip install -r requirements.txt
	```

3. **Start the backend (RAG)**  
	Run the main backend script:
	```powershell
	python main.py
	```

4. **Install Node.js dependencies for the frontend**  
	Navigate to the `app` directory and install dependencies:
	```powershell
	cd ../app
	npm install
	```

5. **Start the frontend**  
	Launch the React app:
	```powershell
	npm start
	```

6. **Access the application**  
	Open your browser and go to [http://localhost:5000](http://localhost:5000) to use the chat bot.

---

## Features

- **Multi-file support:** You can upload multiple files. Each file is stored separately and indexed in its own database table.
- **File management:** Use the burger menu in the chat input to view and delete files. Deleting a file also removes its data from the database.
- **Contextual search:** Ask questions about a specific file by mentioning its name in your message. The bot will automatically search in the relevant file's data.

---

## Example: Asking the AI about a file

Suppose you uploaded a file named `alice_in_wonderland.md`. You can ask:

```
Who is the main character in alice_in_wonderland?
```

Or for another file:

```
What is the topic of test_1?
```

The bot will automatically search in the mentioned file.

---

**Note:**
- Make sure you have Python and Node.js installed on your system.
- For any configuration, check the `backend/config.py` file.