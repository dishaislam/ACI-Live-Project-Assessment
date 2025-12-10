import { User, Bot } from 'lucide-react';
import './MessageList.css';

interface Message {
  id: number;
  role: string;
  content: string;
  image_path: string | null;
  created_at: string;
}

interface MessageListProps {
  messages: Message[];
}

export default function MessageList({ messages }: MessageListProps) {
  if (messages.length === 0) {
    return (
      <div className="no-messages">
        <p>No messages yet. Start a conversation!</p>
      </div>
    );
  }

  return (
    <div className="message-list">
      {messages.map((message) => (
        <div
          key={message.id}
          className={`message ${message.role === 'user' ? 'user-message' : 'assistant-message'}`}
        >
          <div className="message-avatar">
            {message.role === 'user' ? <User size={24} /> : <Bot size={24} />}
          </div>
          
          <div className="message-content">
            {message.image_path && (
              <div className="message-image">
                <img
                  src={`http://localhost:8000/${message.image_path}`}
                  alt="Uploaded"
                  loading="lazy"
                />
              </div>
            )}
            
            <div className="message-text">
              {message.content}
            </div>
            
            <div className="message-time">
              {new Date(message.created_at).toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit'
              })}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
