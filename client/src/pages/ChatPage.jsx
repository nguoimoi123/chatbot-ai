import React, { useState, useRef, useEffect } from 'react'

export default function ChatPage({ user }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [conversations, setConversations] = useState([])
  const [currentConversationId, setCurrentConversationId] = useState(null)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [guestMode, setGuestMode] = useState(false)
  const [personality, setPersonality] = useState('neutral') // Thêm state cho tính cách
  const messagesEndRef = useRef(null)

  const isLoggedIn = !!user

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    if (isLoggedIn) {
      loadConversations()
    }
  }, [isLoggedIn])

  const loadConversations = async () => {
    if (!isLoggedIn) return
    try {
      const response = await fetch('/api/conversations', {
        credentials: 'include'
      })
      if (response.ok) {
        const data = await response.json()
        setConversations(data)
      }
    } catch (error) {
      console.error('Failed to load conversations:', error)
    }
  }

  const loadConversation = async (conversationId) => {
    if (!isLoggedIn) return
    try {
      const response = await fetch(`/api/conversations/${conversationId}`, {
        credentials: 'include'
      })
      if (response.ok) {
        const data = await response.json()
        setMessages(data.messages || [])
        setCurrentConversationId(conversationId)
      }
    } catch (error) {
      console.error('Failed to load conversation:', error)
    }
  }

  const handleNewChat = () => {
    setMessages([])
    setCurrentConversationId(null)
  }

  const handleDeleteConversation = async (conversationId, e) => {
    e.stopPropagation()
    if (!confirm('Bạn có chắc muốn xóa cuộc trò chuyện này?')) return
    
    try {
      const response = await fetch(`/api/conversations/${conversationId}`, {
        method: 'DELETE',
        credentials: 'include'
      })
      if (response.ok) {
        loadConversations()
        if (currentConversationId === conversationId) {
          handleNewChat()
        }
      }
    } catch (error) {
      console.error('Failed to delete conversation:', error)
    }
  }

  const handleSend = async () => {
    if (!input.trim() || loading) return
    const userMessage = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setLoading(true)

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ 
          message: userMessage,
          conversation_id: isLoggedIn ? currentConversationId : null,
          personality: personality // Thêm personality vào request
        })
      })

      if (!response.ok) throw new Error('Failed to send message')
      const data = await response.json()
      setMessages(prev => [...prev, { role: 'assistant', content: data.reply }])
      
      if (data.guest_mode) {
        setGuestMode(true)
      }
      
      if (isLoggedIn && data.conversation_id && !currentConversationId) {
        setCurrentConversationId(data.conversation_id)
        loadConversations()
      }
    } catch (error) {
      console.error('Chat error:', error)
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại.' 
      }])
    } finally {
      setLoading(false)
    }
  }

  const handleLogin = () => {
    window.location.href = '/'
  }

  const handleLogout = () => {
    window.location.href = '/auth/logout'
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50 flex">
      {/* Sidebar - Only show for logged in users */}
      {isLoggedIn && (
        <div className={`${sidebarOpen ? 'w-64' : 'w-0'} transition-all duration-300 bg-white border-r border-gray-200 flex flex-col overflow-hidden`} style={{ height: '100vh' }}>
          <div className="p-4 border-b border-gray-200 flex-shrink-0">
            <button
              onClick={handleNewChat}
              className="w-full px-4 py-3 bg-gradient-to-br from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all duration-300 font-medium shadow-md flex items-center justify-center space-x-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              <span>New Chat</span>
            </button>
          </div>

          <div className="flex-1 overflow-hidden flex flex-col">
            <div className="px-3 py-2 flex-shrink-0">
              <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
                Lịch sử chat
              </h3>
            </div>
            <div className="flex-1 overflow-y-auto p-2">
              <div className="space-y-1">
                {conversations.map((conv) => (
                  <div
                    key={conv.id}
                    onClick={() => loadConversation(conv.id)}
                    className={`group px-3 py-2 rounded-lg cursor-pointer transition-colors flex items-center justify-between ${
                      currentConversationId === conv.id
                        ? 'bg-purple-50 text-purple-700'
                        : 'hover:bg-gray-100 text-gray-700'
                    }`}
                  >
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{conv.title}</p>
                      <p className="text-xs text-gray-500">{conv.message_count} tin nhắn</p>
                    </div>
                    <button
                      onClick={(e) => handleDeleteConversation(conv.id, e)}
                      className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-100 rounded transition-opacity"
                    >
                      <svg className="w-4 h-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
            <div className="flex items-center space-x-4">
              {isLoggedIn && (
                <button
                  onClick={() => setSidebarOpen(!sidebarOpen)}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                  </svg>
                </button>
              )}
              <div className="w-10 h-10 bg-gradient-to-br from-purple-600 to-pink-600 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">FootBallGPT</h1>
                <p className="text-sm text-gray-500">AI Assistant</p>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              {isLoggedIn ? (
                <>
                  {user.profile_image_url && (
                    <img src={user.profile_image_url} alt="Profile" className="w-8 h-8 rounded-full object-cover" />
                  )}
                  <div className="hidden sm:block">
                    <p className="text-sm font-medium text-gray-900">
                      {user.first_name || user.email || 'User'}
                    </p>
                    {user.email && (
                      <p className="text-xs text-gray-500">{user.email}</p>
                    )}
                  </div>
                  <button
                    onClick={handleLogout}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    Đăng xuất
                  </button>
                </>
              ) : (
                <button
                  onClick={handleLogin}
                  className="px-6 py-2 text-sm font-medium text-white bg-gradient-to-br from-purple-600 to-pink-600 rounded-lg hover:from-purple-700 hover:to-pink-700 transition-colors shadow-md"
                >
                  Đăng nhập
                </button>
              )}
            </div>
          </div>
        </header>

        {/* Guest Mode Banner */}
        {!isLoggedIn && (
          <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-4 py-3 text-center">
            <p className="text-sm">
              💡 Bạn đang dùng chế độ khách. 
              <button 
                onClick={handleLogin}
                className="ml-2 underline font-semibold hover:text-purple-100"
              >
                Đăng nhập
              </button> để lưu lịch sử chat và xem lại các cuộc trò chuyện trước.
            </p>
          </div>
        )}

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto px-4 py-8">
          <div className="max-w-4xl mx-auto space-y-6">
            {messages.length === 0 ? (
              <div className="text-center py-12">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-purple-600 to-pink-600 rounded-full mb-4">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  Xin chào! Tôi có thể giúp gì cho bạn?
                </h3>
                <p className="text-gray-500">Hãy nhập câu hỏi bên dưới để bắt đầu trò chuyện</p>
                {!isLoggedIn && (
                  <p className="text-sm text-purple-600 mt-4">
                    Bạn có thể chat ngay mà không cần đăng nhập!
                  </p>
                )}
              </div>
            ) : (
              messages.map((m, i) => (
                <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-3xl px-6 py-4 rounded-2xl ${
                    m.role === 'user'
                      ? 'bg-gradient-to-br from-purple-600 to-pink-600 text-white'
                      : 'bg-white shadow-md border border-gray-100 text-gray-800'
                  }`}>
                    <p className="whitespace-pre-wrap">{m.content}</p>
                  </div>
                </div>
              ))
            )}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-white shadow-md px-6 py-4 rounded-2xl border border-gray-100">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="bg-white border-t border-gray-200 px-4 py-6">
          <div className="max-w-4xl mx-auto space-y-4">
            {/* Personality Selector */}
            <div>
              <p className="text-xs font-semibold text-gray-500 uppercase mb-2 text-center">
                Chọn tính cách chatbot
              </p>
              <div className="flex flex-wrap gap-2 justify-center">
                <button
                  onClick={() => setPersonality('neutral')}
                  className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
                    personality === 'neutral'
                      ? 'bg-gray-600 text-white shadow-md'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  ⚽ Trung lập
                </button>
                <button
                  onClick={() => setPersonality('ronaldo')}
                  className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
                    personality === 'ronaldo'
                      ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-md'
                      : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                  }`}
                >
                  🐐 Fan Ronaldo
                </button>
                <button
                  onClick={() => setPersonality('messi')}
                  className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
                    personality === 'messi'
                      ? 'bg-gradient-to-r from-pink-500 to-yellow-500 text-white shadow-md'
                      : 'bg-pink-100 text-pink-700 hover:bg-pink-200'
                  }`}
                >
                  ✨ Fan Messi
                </button>
                <button
                  onClick={() => setPersonality('manutd')}
                  className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
                    personality === 'manutd'
                      ? 'bg-gradient-to-r from-red-600 to-red-800 text-white shadow-md'
                      : 'bg-red-100 text-red-700 hover:bg-red-200'
                  }`}
                >
                  👹 Fan Man Utd
                </button>
              </div>
            </div>
            
            {/* Chat Input */}
            <div className="flex items-center space-x-4">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
                placeholder="Nhập câu hỏi của bạn..."
                className="flex-1 px-6 py-4 bg-gray-100 border border-gray-200 rounded-full focus:outline-none focus:ring-2 focus:ring-purple-500"
                disabled={loading}
              />
              <button
                onClick={handleSend}
                disabled={!input.trim() || loading}
                className="px-8 py-4 bg-gradient-to-br from-purple-600 to-pink-600 text-white rounded-full hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 transition-all duration-300 font-medium shadow-lg"
              >
                {loading ? 'Đang gửi...' : 'Gửi'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}