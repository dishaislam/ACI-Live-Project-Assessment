import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import Sidebar from '../components/Sidebar';
import MessageList from '../components/MessageList';
import MessageInput from '../components/MessageInput';
import './Chat.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface Message {
  id: number;
  session_id: number;
  role: string;
  content: string;
  image_path: string | null;
  created_at: string;
}

interface ChatSession {
  id: number;
  user_id: number;
  title: string;
  created_at: string;
  updated_at: string;
}

export default function Chat() {
  const { user, logout } = useAuth();
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Fetch sessions on mount
  useEffect(() => {
    fetchSessions();
  }, []);

  // Fetch messages when session changes
  useEffect(() => {
    if (currentSession) {
      fetchMessages(currentSession.id);
    } else {
      setMessages([]);
    }
  }, [currentSession]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchSessions = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/chat/sessions`);
      setSessions(response.data);
      
      // If no current session and sessions exist, select the first one
      if (!currentSession && response.data.length > 0) {
        setCurrentSession(response.data[0]);
      }
    } catch (error) {
      console.error('Failed to fetch sessions:', error);
    }
  };

  const fetchMessages = async (sessionId: number) => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/api/chat/sessions/${sessionId}/messages`);
      setMessages(response.data);
    } catch (error) {
      console.error('Failed to fetch messages:', error);
    } finally {
      setLoading(false);
    }
  };

  const createNewSession = async () => {
    try {
      const response = await axios.post(`${API_URL}/api/chat/sessions`);
      const newSession = response.data;
      setSessions([newSession, ...sessions]);
      setCurrentSession(newSession);
    } catch (error) {
      console.error('Failed to create session:', error);
    }
  };

  const deleteSession = async (sessionId: number) => {
    try {
      await axios.delete(`${API_URL}/api/chat/sessions/${sessionId}`);
      setSessions(sessions.filter(s => s.id !== sessionId));
      
      if (currentSession?.id === sessionId) {
        setCurrentSession(sessions.length > 1 ? sessions[0] : null);
      }
    } catch (error) {
      console.error('Failed to delete session:', error);
    }
  };

  const sendMessage = async (text: string, image: File | null) => {
    if (!currentSession) {
      await createNewSession();
      return;
    }

    setSending(true);
    
    try {
      const formData = new FormData();
      formData.append('text', text);
      if (image) {
        formData.append('image', image);
      }

      const response = await axios.post(
        `${API_URL}/api/chat/sessions/${currentSession.id}/messages`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      // Refresh messages to get both user and assistant messages
      await fetchMessages(currentSession.id);
      
      // Update sessions list to reflect new timestamp
      await fetchSessions();
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="chat-container">
      <Sidebar
        sessions={sessions}
        currentSession={currentSession}
        onSessionSelect={setCurrentSession}
        onNewSession={createNewSession}
        onDeleteSession={deleteSession}
        user={user}
        onLogout={logout}
      />
      
      <div className="chat-main">
        {currentSession ? (
          <>
            <div className="chat-header">
              <h2>{currentSession.title}</h2>
            </div>
            
            <div className="chat-messages">
              {loading ? (
                <div className="loading-messages">Loading messages...</div>
              ) : (
                <MessageList messages={messages} />
              )}
              <div ref={messagesEndRef} />
            </div>
            
            <MessageInput onSend={sendMessage} disabled={sending} />
          </>
        ) : (
          <div className="chat-empty">
            <h2>Welcome to Multimodal Chat</h2>
            <p>Create a new chat session to get started</p>
            <button onClick={createNewSession} className="create-session-btn">
              New Chat
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
