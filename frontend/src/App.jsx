import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([{
    role: 'assistant',
    content: 'Hello! I\'m your study assistant. How can I help you today?'
  }]);
  const [input, setInput] = useState('');
  const [image, setImage] = useState(null);
  const [isTyping, setIsTyping] = useState(false);
  const [imagePreviewing, setImagePreviewing] = useState(null);
  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  // Focus input when chat opens
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => {
        inputRef.current?.focus();
      }, 300);
    }
  }, [isOpen]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() && !image) return;
   
    const userMessage = { 
      role: 'user', 
      content: input,
      image: imagePreviewing 
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);
   
    try {
      const formData = new FormData();
      formData.append('message', input);
      if (image) formData.append('image', image);
     
      const response = await axios.post('http://localhost:8000/api/chat/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
     
      // Simulate a slight delay for natural conversation flow
      setTimeout(() => {
        setMessages(prev => [...prev, { role: 'assistant', content: response.data.answer }]);
        setIsTyping(false);
      }, 700);
    } catch (error) {
      setTimeout(() => {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.'
        }]);
        setIsTyping(false);
      }, 700);
    }
   
    setImage(null);
    setImagePreviewing(null);
  };

  const handleFileChange = (e) => {
    if (e.target.files[0]) {
      setImage(e.target.files[0]);
      setImagePreviewing(URL.createObjectURL(e.target.files[0]));
    }
  };

  const handleClearImage = () => {
    setImage(null);
    setImagePreviewing(null);
  };

  // Enhanced message rendering with proper formatting
  const renderMessage = (content) => {
    return {
      __html: content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br />')
    };
  };

  return (
    <div className="chat-system">
      <img
        src="/chatbot.png" // Make sure this path is correct
        alt="Chat Assistant"
        className="chatbot-icon"
        onClick={() => setIsOpen(!isOpen)}
      />
     
      <div className={`chat-popup ${isOpen ? 'show' : ''}`}>
        <div className="chat-header">
          <h3>Study Assistant</h3>
          <button onClick={() => setIsOpen(false)} aria-label="Close chat">×</button>
        </div>
       
        <div className="messages">
          {messages.map((msg, i) => (
            <div key={i} className={`message ${msg.role}`}>
              {msg.image && <img src={msg.image} alt="Uploaded content" />}
              <p dangerouslySetInnerHTML={renderMessage(msg.content)} />
            </div>
          ))}
          {isTyping && (
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
       
        {imagePreviewing && (
          <div className="image-preview">
            <img src={imagePreviewing} alt="Preview" />
            <button onClick={handleClearImage} className="remove-image" aria-label="Remove image">×</button>
          </div>
        )}
       
        <form onSubmit={handleSubmit} className="chat-input">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your question..."
            ref={inputRef}
          />
          <button
            type="button"
            onClick={() => fileInputRef.current.click()}
            className="upload-btn"
            title="Upload image"
            aria-label="Upload image"
          >
            📎
          </button>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept="image/*"
            style={{ display: 'none' }}
          />
          <button 
            type="submit" 
            className="send-btn" 
            title="Send message"
            aria-label="Send message"
            disabled={!input.trim() && !image}
          >
            ➤
          </button>
        </form>
      </div>
    </div>
  );
}

export default App;