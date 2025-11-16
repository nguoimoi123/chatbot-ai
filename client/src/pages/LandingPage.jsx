import React ,{ useState }from 'react'

export default function LandingPage() {
  const [showOptions, setShowOptions] = useState(false)
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL
  const handleGoogle = () => {
  window.location.href = `${API_BASE_URL}/login/google`;
}
  const handleGithub = () => {window.location.href = `${API_BASE_URL}/login/github`}
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-600 via-pink-500 to-red-500 flex items-center justify-center p-4">
      <div className="max-w-4xl w-full">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <div className="mb-6">
            <div className="inline-flex items-center justify-center w-24 h-24 bg-white rounded-full shadow-2xl mb-6">
              <svg className="w-12 h-12 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            </div>
          </div>
          
          <h1 className="text-6xl md:text-7xl font-bold text-white mb-6 tracking-tight">
            FootBallGPT
          </h1>
          
          <p className="text-xl md:text-2xl text-white/90 mb-8 max-w-2xl mx-auto">
            Trợ lý AI thông minh với khả năng tra cứu dữ liệu thời gian thực
          </p>

          <div className="flex flex-wrap gap-4 justify-center mb-12">
            <div className="bg-white/10 backdrop-blur-md rounded-lg px-6 py-3 text-white">
              ⚡ Phản hồi nhanh
            </div>
            <div className="bg-white/10 backdrop-blur-md rounded-lg px-6 py-3 text-white">
              🎯 Chính xác cao
            </div>
            <div className="bg-white/10 backdrop-blur-md rounded-lg px-6 py-3 text-white">
              🔒 Bảo mật
            </div>
          </div>

 {!showOptions ? (
          <button 
            onClick={() => setShowOptions(true)}
            className="group relative inline-flex items-center justify-center px-8 py-4 text-lg font-semibold text-purple-600 bg-white rounded-full hover:bg-gray-50 transition-all duration-300 shadow-2xl hover:shadow-purple-500/50 hover:scale-105"
          >
            <span>Đăng nhập để bắt đầu</span>
            <svg className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </button>
        ) : (
          <div className="flex flex-col sm:flex-row justify-center gap-4 mt-6">
            <button
              onClick={handleGoogle}
              className="px-6 py-3 bg-white text-purple-600 rounded-full font-semibold hover:bg-gray-100 transition-colors shadow-md"
            >
              Đăng nhập với Google
            </button>
            <button
              onClick={handleGithub}
              className="px-6 py-3 bg-gray-900 text-white rounded-full font-semibold hover:bg-gray-800 transition-colors shadow-md"
            >
              Đăng nhập với GitHub
            </button>
          </div>
        )}


          <p className="mt-6 text-white/70 text-sm">
            Hỗ trợ đăng nhập bằng Google, GitHub, X, Apple, và Email
          </p>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-6 mt-16">
          <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 text-white hover:bg-white/20 transition-all duration-300">
            <div className="text-4xl mb-4">🧠</div>
            <h3 className="text-xl font-semibold mb-2">RAG Technology</h3>
            <p className="text-white/80">Kết hợp AI với dữ liệu thực tế để đưa ra câu trả lời chính xác nhất</p>
          </div>

          <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 text-white hover:bg-white/20 transition-all duration-300">
            <div className="text-4xl mb-4">💬</div>
            <h3 className="text-xl font-semibold mb-2">Lưu lịch sử</h3>
            <p className="text-white/80">Theo dõi tất cả cuộc trò chuyện của bạn một cách an toàn</p>
          </div>

          <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 text-white hover:bg-white/20 transition-all duration-300">
            <div className="text-4xl mb-4">⚙️</div>
            <h3 className="text-xl font-semibold mb-2">Đa nền tảng</h3>
            <p className="text-white/80">Sử dụng mọi lúc mọi nơi trên mọi thiết bị</p>
          </div>
        </div>
      </div>
    </div>
  )
}
