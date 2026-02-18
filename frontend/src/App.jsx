import { useState } from 'react';
import axios from 'axios';
import { Send, Upload, FileText, Loader2, Bot, User } from 'lucide-react';

function App() {
  const [file, setFile] = useState(null);
  const [messages, setMessages] = useState([
    { role: 'bot', text: "Hello! Upload a PDF document to start chatting." }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState("idle"); // idle, uploading, done

  // 1. Handle File Selection
  const handleFileChange = (e) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  };

  // 2. Handle File Upload to Backend
  const handleUpload = async () => {
    if (!file) return;
    setUploadStatus("uploading");
    
    const formData = new FormData();
    formData.append("file", file);

    try {
      // Connect to your FastAPI Backend
      await axios.post("https://anjil-talk-with-pdf.hf.space/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setUploadStatus("done");
      setMessages(prev => [...prev, { role: 'bot', text: "PDF uploaded! I'm ready for your questions." }]);
    } catch (error) {
      console.error("Upload failed:", error);
      setUploadStatus("idle");
      alert("Upload failed. Is the backend running?");
    }
  };

  // 3. Handle Chat Message
  const sendMessage = async () => {
    if (!input.trim()) return;

    // Add user message immediately
    const userMessage = { role: 'user', text: input };
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      // Send question to Backend
      const response = await axios.post("https://anjil-talk-with-pdf.hf.space/chat", {
        question: userMessage.text
      });

      // Add bot response
      const botMessage = { role: 'bot', text: response.data.answer };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error("Chat failed:", error);
      setMessages(prev => [...prev, { role: 'bot', text: "Sorry, I couldn't reach the brain." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-900 text-white font-sans">
      
      {/* LEFT SIDEBAR - Upload Area */}
      <div className="w-1/4 bg-gray-800 p-6 flex flex-col border-r border-gray-700">
        <h1 className="text-2xl font-bold mb-8 text-blue-400 flex items-center gap-2">
          <FileText /> TalkWithPDF
        </h1>
        
        <div className="bg-gray-700 p-6 rounded-lg border-2 border-dashed border-gray-600 text-center">
          <input 
            type="file" 
            accept=".pdf"
            onChange={handleFileChange}
            className="hidden" 
            id="file-upload"
          />
          <label htmlFor="file-upload" className="cursor-pointer block">
            <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
            <span className="text-sm text-gray-300">
              {file ? file.name : "Click to select PDF"}
            </span>
          </label>
        </div>

        <button 
          onClick={handleUpload}
          disabled={!file || uploadStatus === 'uploading'}
          className={`mt-4 w-full py-2 rounded-lg font-semibold transition-colors ${
            uploadStatus === 'done' 
              ? 'bg-green-600 text-white' 
              : 'bg-blue-600 hover:bg-blue-500 text-white'
          }`}
        >
          {uploadStatus === 'uploading' ? 'Uploading...' : uploadStatus === 'done' ? 'Uploaded!' : 'Upload PDF'}
        </button>
      </div>

      {/* RIGHT MAIN AREA - Chat Interface */}
      <div className="flex-1 flex flex-col">
        {/* Chat Messages */}
        <div className="flex-1 p-6 overflow-y-auto space-y-4">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] p-4 rounded-xl flex gap-3 ${
                msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-200'
              }`}>
                {msg.role === 'bot' ? <Bot size={20} /> : <User size={20} />}
                <p className="text-sm leading-relaxed">{msg.text}</p>
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-gray-700 p-4 rounded-xl flex items-center gap-2">
                <Loader2 className="animate-spin w-4 h-4" />
                <span className="text-xs text-gray-400">Thinking...</span>
              </div>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="p-4 bg-gray-800 border-t border-gray-700">
          <div className="flex gap-2 max-w-4xl mx-auto">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Ask a question about your PDF..."
              className="flex-1 bg-gray-700 border-none rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-blue-500 outline-none"
            />
            <button 
              onClick={sendMessage}
              disabled={loading}
              className="bg-blue-600 hover:bg-blue-500 px-6 rounded-lg text-white transition-colors"
            >
              <Send size={20} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;