# Frontend - Multimodal Chat Application

React + TypeScript frontend for the Multimodal Chat Application.

## 📁 Project Structure

```
frontend/
├── public/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── Sidebar.tsx      # Chat session sidebar
│   │   ├── Sidebar.css
│   │   ├── MessageList.tsx  # Message display
│   │   ├── MessageList.css
│   │   ├── MessageInput.tsx # Text + image input
│   │   └── MessageInput.css
│   │
│   ├── contexts/            # React Context providers
│   │   └── AuthContext.tsx  # Authentication state
│   │
│   ├── pages/              # Page components
│   │   ├── Login.tsx       # Login page
│   │   ├── Register.tsx    # Registration page
│   │   ├── Chat.tsx        # Main chat interface
│   │   ├── Chat.css
│   │   └── Auth.css        # Shared auth styles
│   │
│   ├── App.tsx             # Main app component
│   ├── App.css
│   ├── main.tsx            # Entry point
│   └── index.css           # Global styles
│
├── index.html              # HTML template
├── package.json            # Dependencies
├── vite.config.ts          # Vite configuration
├── tsconfig.json           # TypeScript config
└── .env.example            # Environment variables template

```

## 🚀 Quick Start

### Prerequisites
- Node.js 18 or higher
- npm or yarn

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Start development server
npm run dev
```

The app will be available at `http://localhost:3000`

## 📦 Dependencies

### Core
- **React 18.2.0** - UI library
- **React Router DOM 6.21.0** - Routing
- **TypeScript 5.2.2** - Type safety

### HTTP & State
- **Axios 1.6.2** - HTTP client
- **React Context API** - State management

### UI & Icons
- **Lucide React 0.294.0** - Icon library

### Build Tools
- **Vite 5.0.8** - Build tool and dev server
- **@vitejs/plugin-react 4.2.1** - React plugin for Vite

## 🔧 Available Scripts

```bash
# Development server with HMR
npm run dev

# Type check
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## 🗂️ Component Overview

### App.tsx
Main application component with routing:
- Sets up React Router
- Provides AuthContext
- Defines routes (Login, Register, Chat)
- Implements ProtectedRoute wrapper

### AuthContext.tsx
Global authentication state management:
- Stores user data and JWT token
- Provides login/register/logout functions
- Persists auth state in localStorage
- Sets Axios authorization headers

### Login.tsx & Register.tsx
Authentication forms:
- Form validation
- Error handling
- Automatic redirect on success
- Links between pages

### Chat.tsx
Main chat interface:
- Session management
- Message fetching and sending
- Real-time updates
- Coordinates child components

### Sidebar.tsx
Session navigation:
- List all chat sessions
- Create new sessions
- Delete sessions
- User profile display
- Logout button

### MessageList.tsx
Message display:
- Renders user and assistant messages
- Displays images
- Shows timestamps
- Auto-scrolls to latest message

### MessageInput.tsx
Message composition:
- Multiline text input
- Image upload with preview
- Drag & drop support
- Send button with loading state
- Keyboard shortcuts (Enter to send)

## 🎨 Styling

The app uses vanilla CSS with a modern design:

### Color Scheme
- **Primary Gradient**: Purple to blue (`#667eea` → `#764ba2`)
- **Dark Sidebar**: `#1a1a1a`
- **Light Chat Area**: `#f8f9fa`
- **Message Bubbles**: White with shadows

### Responsive Design
- Mobile-first approach
- Flexible layouts
- Responsive typography
- Touch-friendly buttons

## 🔐 Authentication Flow

```
1. User visits app → Check localStorage for token
2. No token → Redirect to /login
3. User logs in → Store token + user data
4. Set Axios default headers
5. Redirect to /chat
6. All API requests include Bearer token
```

## 📡 API Integration

### Base Configuration

```typescript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

### Axios Setup

```typescript
// Set default authorization header
axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
```

### API Endpoints Used

**Authentication:**
- `POST /api/auth/register` - Create account
- `POST /api/auth/login` - Login

**Chat Sessions:**
- `GET /api/chat/sessions` - List sessions
- `POST /api/chat/sessions` - Create session
- `DELETE /api/chat/sessions/:id` - Delete session

**Messages:**
- `GET /api/chat/sessions/:id/messages` - Get messages
- `POST /api/chat/sessions/:id/messages` - Send message (FormData)

## 🖼️ Image Upload

### File Handling

```typescript
// Accept images only
<input type="file" accept="image/*" />

// Validate file type
if (!file.type.startsWith('image/')) {
  alert('Please select an image file');
  return;
}

// Validate file size (10MB max)
if (file.size > 10 * 1024 * 1024) {
  alert('Image size must be less than 10MB');
  return;
}
```

### FormData Upload

```typescript
const formData = new FormData();
formData.append('text', text);
formData.append('image', imageFile);

await axios.post(url, formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
});
```

## 🔄 State Management

### Global State (AuthContext)
- User data
- Authentication status
- Login/logout functions

### Local State (Component)
- Form inputs
- Loading states
- Error messages
- UI toggles

### Server State
- Chat sessions (fetched from API)
- Messages (fetched from API)
- No caching layer (can be added with React Query)

## 🎯 Key Features

### Auto-scroll
Messages automatically scroll to bottom when new messages arrive:
```typescript
useEffect(() => {
  messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
}, [messages]);
```

### Image Preview
Show image preview before sending:
```typescript
const reader = new FileReader();
reader.onloadend = () => {
  setImagePreview(reader.result as string);
};
reader.readAsDataURL(file);
```

### Keyboard Shortcuts
- **Enter**: Send message
- **Shift + Enter**: New line

### Session Timestamps
Display relative time (e.g., "2h ago", "3d ago"):
```typescript
const diffMins = Math.floor((now - date) / 60000);
if (diffMins < 60) return `${diffMins}m ago`;
```

## 🌐 Environment Variables

Create `.env` file:

```env
VITE_API_URL=http://localhost:8000
```

Access in code:
```typescript
const API_URL = import.meta.env.VITE_API_URL;
```

## 🏗️ Build for Production

```bash
# Build
npm run build

# Output directory: dist/
# Contains optimized HTML, CSS, JS
# Ready to deploy to any static host
```

### Deployment Options
- **Vercel**: `vercel deploy`
- **Netlify**: Drag & drop `dist/` folder
- **GitHub Pages**: Configure in repo settings
- **Nginx**: Serve `dist/` directory

## 🐛 Common Issues

### CORS Errors
**Problem**: API requests blocked by CORS
**Solution**: Backend CORS must allow frontend origin

### Token Expired
**Problem**: 401 Unauthorized errors
**Solution**: Implement token refresh or re-login

### Image Not Loading
**Problem**: Images don't display after upload
**Solution**: Check image path and backend static file serving

### Hot Reload Not Working
**Problem**: Changes don't reflect in browser
**Solution**: Restart dev server, clear cache

## 🔍 Development Tips

### VS Code Extensions
- ESLint
- Prettier
- TypeScript and JavaScript Language Features
- ES7+ React/Redux/React-Native snippets

### TypeScript Tips
- Use `interface` for props
- Enable strict mode
- Use type inference where possible
- Avoid `any` type

### Component Best Practices
- Keep components small and focused
- Extract reusable logic to hooks
- Use proper TypeScript types
- Add loading and error states

## 📱 Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## 🧪 Testing (Future)

Recommended testing setup:
```bash
npm install --save-dev @testing-library/react @testing-library/jest-dom vitest
```

Example test:
```typescript
import { render, screen } from '@testing-library/react';
import { Login } from './Login';

test('renders login form', () => {
  render(<Login />);
  expect(screen.getByText('Welcome Back')).toBeInTheDocument();
});
```

## 🚀 Performance Optimization

### Current Optimizations
- Vite's fast HMR
- Code splitting by route
- Optimized production build

### Future Improvements
- React.memo for expensive components
- Virtual scrolling for long message lists
- Image lazy loading
- Service worker for offline support

## 📚 Additional Resources

- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Vite Guide](https://vitejs.dev/guide/)
- [React Router Docs](https://reactrouter.com/)

## 🤝 Contributing

When adding new features:
1. Create feature branch
2. Add TypeScript types
3. Follow existing code style
4. Test thoroughly
5. Update documentation

## 📄 License

MIT License - See LICENSE file for details
