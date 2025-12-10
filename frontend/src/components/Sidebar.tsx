import { MessageSquare, Plus, Trash2, LogOut } from 'lucide-react';
import './Sidebar.css';

interface ChatSession {
  id: number;
  title: string;
  updated_at: string;
}

interface User {
  username: string;
  email: string;
}

interface SidebarProps {
  sessions: ChatSession[];
  currentSession: ChatSession | null;
  onSessionSelect: (session: ChatSession) => void;
  onNewSession: () => void;
  onDeleteSession: (sessionId: number) => void;
  user: User | null;
  onLogout: () => void;
}

export default function Sidebar({
  sessions,
  currentSession,
  onSessionSelect,
  onNewSession,
  onDeleteSession,
  user,
  onLogout,
}: SidebarProps) {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) {
      return `${diffMins}m ago`;
    } else if (diffHours < 24) {
      return `${diffHours}h ago`;
    } else if (diffDays < 7) {
      return `${diffDays}d ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h1>Multimodal Chat</h1>
        <button onClick={onNewSession} className="new-chat-btn" title="New Chat">
          <Plus size={20} />
        </button>
      </div>

      <div className="sessions-list">
        {sessions.map((session) => (
          <div
            key={session.id}
            className={`session-item ${currentSession?.id === session.id ? 'active' : ''}`}
            onClick={() => onSessionSelect(session)}
          >
            <div className="session-content">
              <MessageSquare size={18} />
              <div className="session-info">
                <span className="session-title">{session.title}</span>
                <span className="session-time">{formatDate(session.updated_at)}</span>
              </div>
            </div>
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDeleteSession(session.id);
              }}
              className="delete-btn"
              title="Delete chat"
            >
              <Trash2 size={16} />
            </button>
          </div>
        ))}
      </div>

      <div className="sidebar-footer">
        <div className="user-info">
          <div className="user-avatar">
            {user?.username.charAt(0).toUpperCase()}
          </div>
          <div className="user-details">
            <span className="user-name">{user?.username}</span>
            <span className="user-email">{user?.email}</span>
          </div>
        </div>
        <button onClick={onLogout} className="logout-btn" title="Logout">
          <LogOut size={18} />
        </button>
      </div>
    </div>
  );
}
