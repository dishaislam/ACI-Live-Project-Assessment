import { useState, useRef } from 'react';
import { Send, Image, X } from 'lucide-react';
import './MessageInput.css';

interface MessageInputProps {
  onSend: (text: string, image: File | null) => void;
  disabled?: boolean;
}

export default function MessageInput({ onSend, disabled }: MessageInputProps) {
  const [text, setText] = useState('');
  const [image, setImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        alert('Please select an image file');
        return;
      }

      // Validate file size (10MB)
      if (file.size > 10 * 1024 * 1024) {
        alert('Image size must be less than 10MB');
        return;
      }

      setImage(file);
      
      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleRemoveImage = () => {
    setImage(null);
    setImagePreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!text.trim() && !image) {
      return;
    }

    onSend(text.trim(), image);
    
    // Reset form
    setText('');
    setImage(null);
    setImagePreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="message-input-container">
      {imagePreview && (
        <div className="image-preview">
          <img src={imagePreview} alt="Preview" />
          <button
            onClick={handleRemoveImage}
            className="remove-image-btn"
            type="button"
          >
            <X size={16} />
          </button>
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="message-input-form">
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleImageSelect}
          style={{ display: 'none' }}
        />
        
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          className="image-btn"
          disabled={disabled}
          title="Upload image"
        >
          <Image size={20} />
        </button>

        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a message... (Shift + Enter for new line)"
          rows={1}
          disabled={disabled}
        />

        <button
          type="submit"
          className="send-btn"
          disabled={disabled || (!text.trim() && !image)}
        >
          {disabled ? (
            <div className="spinner" />
          ) : (
            <Send size={20} />
          )}
        </button>
      </form>
    </div>
  );
}
