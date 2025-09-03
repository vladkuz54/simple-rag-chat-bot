import React, { useState, useEffect } from 'react';
import { FiMenu, FiX } from 'react-icons/fi';
import './App.css';
import { FiPaperclip } from 'react-icons/fi';
import { IoMdSend } from 'react-icons/io';

function ThrobberDots() {
  const [dots, setDots] = useState('');
  useEffect(() => {
    const interval = setInterval(() => {
      setDots(prev => (prev.length < 3 ? prev + '.' : ''));
    }, 500);
    return () => clearInterval(interval);
  }, []);
  return <span className="dots-throbber">{dots}</span>;
}

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [waitingAnswer, setWaitingAnswer] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [files, setFiles] = useState([]);

  useEffect(() => {
    setMessages([
      { text: 'Hi! Please send me a file.', sender: 'ai' }
    ]);
  }, []);

  const fetchFiles = async () => {
    try {
      const res = await fetch('http://localhost:5000/status');
      const data = await res.json();
      setFiles(data.files || []);
    } catch {}
  };

  const handleDeleteFile = async (filename) => {
    try {
      await fetch('http://localhost:5000/delete_file', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename })
      });
      setFiles(prev => prev.filter(f => f !== filename));
      setMessages(prev => [...prev, { text: `File ${filename} deleted.`, sender: 'ai' }]);
    } catch {
      setMessages(prev => [...prev, { text: `Error: Could not delete file ${filename}.`, sender: 'ai' }]);
    }
  };

  const handleSend = async () => {
    if (input.trim()) {
      const userMsg = { text: input, sender: 'user' };
      setMessages(prev => [...prev, userMsg]);
      setInput('');
      setWaitingAnswer(true); 
      try {
        const res = await fetch('http://localhost:5000/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question: input })
        });
        const data = await res.json();
        if (data.answer) {
          setMessages(prev => [...prev, { text: data.answer, sender: 'ai' }]);
        }
      } catch (err) {
        setMessages(prev => [...prev, { text: 'Error: Could not get answer from server.', sender: 'ai' }]);
      }
      setWaitingAnswer(false);
    }
    if (file) {
      handleFileSend();
    }
  };

  const handleFileSend = async () => {
    if (!file) return;
    setLoading(true);

    setMessages(prev => [...prev, { text: `📎 ${file.name}`, sender: 'user', file }]);
    setFile(null);

    setMessages(prev => [...prev, { text: '', sender: 'ai', throbber: true }]);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      setMessages(prev => [
        ...prev.filter(msg => !msg.throbber),
        { text: data.message || 'File uploaded.', sender: 'ai' }
      ]);
    } catch (err) {
      setMessages(prev => [
        ...prev.filter(msg => !msg.throbber),
        { text: 'Error: Could not upload file.', sender: 'ai' }
      ]);
    }
    setLoading(false); 
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const FileListModal = ({ open, files, onClose, onDelete }) => {
    if (!open) return null;
    return (
      <div className="modal-overlay" onClick={onClose}>
        <div className="modal-window" onClick={e => e.stopPropagation()}>
          <div className="modal-header">
            <span>Files</span>
          </div>
          <ul className="file-list">
            {files.map((file, idx) => (
              <li key={file} className="file-list-item">
                <span className="file-name">{file}</span>
                <span className="file-delete" onClick={() => onDelete(file)} title="Delete"><FiX /></span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    );
  };

  return (
    <main>
      <div className='chat-window'>
        <div className="chat">
          {messages.map((msg, idx) => (
            <div key={idx} className={msg.sender === 'user' ? 'msg-user' : 'msg-ai'}>
              {msg.throbber ? <ThrobberDots /> : msg.text}
            </div>
          ))}
          {waitingAnswer && (
            <div className="msg-ai">
              <ThrobberDots />
            </div>
          )}
        </div>
        <div className="input-area" style={{ position: 'relative' }}>
          <button
            className="burger-btn"
            style={{ position: 'relative', zIndex: 2 }}
            onClick={() => {
              if (!modalOpen) fetchFiles();
              setModalOpen(prev => !prev);
            }}
          >
            <FiMenu size={28} />
          </button>
          {modalOpen && (
            <div style={{ position: 'absolute', bottom: '48px', left: 0, width: '100%', zIndex: 10 }}>
              <FileListModal
                open={true}
                files={files}
                onClose={() => setModalOpen(false)}
                onDelete={handleDeleteFile}
              />
            </div>
          )}
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Enter your message..."
            onKeyDown={e => {
              if (e.key === 'Enter') {
                handleSend();
              }
            }}
          />
          <input
            type="file"
            id="file-input"
            style={{ display: 'none' }}
            onChange={handleFileChange}
          />
          <button onClick={() => document.getElementById('file-input').click()}>
            <FiPaperclip />
          </button>
          <button onClick={handleSend}>
            <IoMdSend />
          </button>
          {file && (
            <span className="selected-file">📎 {file.name}</span>
          )}
        </div>
      </div>
    </main>
  );
}

export default App;
