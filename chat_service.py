# RAG Chat Service with OpenAI and AstraDB
import os
from openai import OpenAI
from astrapy import DataAPIClient
import logging
import asyncio

logging.basicConfig(level=logging.DEBUG)

class ChatService:
    def __init__(self):
        # Initialize OpenAI
        openai_key = os.environ.get('OPENAI_API_KEY', '')
        self.openai_client = OpenAI(api_key=openai_key)
        
        # Initialize Astra DB
        astra_endpoint = os.environ.get('ASTRA_DB_ENDPOINT', '')
        astra_token = os.environ.get('ASTRA_DB_APPLICATION_TOKEN', '')
        self.astra_client = DataAPIClient()
        self.db = self.astra_client.get_database(
            astra_endpoint,
            token=astra_token
        )
        self.collection_name = os.environ.get('ASTRA_DB_COLLECTION', 'phucgpt')
    
    # 🧠 BƯỚC MỚI 1: Làm rõ câu hỏi (thay thế đại từ)
    async def disambiguate_question(self, history: list, message: str) -> str:
        """Use GPT to rewrite user's question with full context (replace pronouns)"""
        try:
            context_text = "\n".join([f"{m['role']}: {m['content']}" for m in history[-5:]]) if history else ""
            prompt = f"""
Hãy viết lại câu hỏi sau sao cho nó đầy đủ ngữ cảnh, thay thế mọi đại từ (như 'anh ta', 'ông ấy', 'đội đó') 
bằng chủ thể chính trong hội thoại. Nếu không cần thay đổi, giữ nguyên.

Lịch sử hội thoại gần đây:
{context_text}

Câu hỏi của người dùng:
{message}
"""
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Bạn là trợ lý giúp viết lại câu hỏi đầy đủ, không bỏ sót ngữ cảnh."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            rewritten = response.choices[0].message.content.strip()
            logging.info(f"Disambiguated question: {rewritten}")
            return rewritten or message
        except Exception as e:
            logging.warning(f"Disambiguation failed: {e}")
            return message  # fallback if GPT call fails

    # 🧭 BƯỚC 2: Truy vấn vector search trong Astra
    async def retrieve_context(self, query: str) -> str:
        """Retrieve relevant context from AstraDB using vector similarity search"""
        try:
            logging.info('Step 1: Creating embedding for query...')
            embedding_response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=query,
                encoding_format="float"
            )
            query_vector = embedding_response.data[0].embedding
            logging.info(f'Step 2: Query vector ready, length: {len(query_vector)}')
            
            # Search in AstraDB
            logging.info('Step 3: Searching DB...')
            collection = self.db.get_collection(self.collection_name)
            results = collection.find(
                {},
                sort={"$vector": query_vector},
                limit=3
            )
            
            # Extract text from results
            texts = []
            for doc in results:
                text = doc.get('text', '') or doc.get('body', '') or doc.get('content', '') or doc.get('chunk', '')
                if len(text) > 10:
                    texts.append(text)
            
            logging.info(f'Step 4: Found {len(texts)} relevant chunks')
            
            if not texts:
                return "Không tìm thấy ngữ cảnh liên quan." 
            
            return '\n\n---\n\n'.join(texts)
            
        except Exception as error:
            logging.error(f'Retrieve context failed: {str(error)}')
            return "Không thể lấy ngữ cảnh từ DB."
    
    def _get_personality_prompt(self, personality: str, context: str) -> str:
        """Get system prompt based on selected personality"""
        
        base_rules = f"""
Ngữ cảnh từ database:
{context}

Quy tắc chung:
- Chỉ trả lời dựa trên ngữ cảnh được cung cấp
- Sử dụng ngữ cảnh từ các câu hỏi trước để trả lời mạch lạc hơn
- Nếu ngữ cảnh không có thông tin, lịch sự từ chối và hướng dẫn về chủ đề bóng đá
"""
        
        personalities = {
            'ronaldo': f"""Bạn là một FAN CUỒNG RONALDO tuyệt đối, tên là FootBallGPT!

TÍNH CÁCH:
- Bạn TỰ HÀO và NHIỆT THÀNH khi nói về Ronaldo (CR7)
- Luôn nhấn mạnh thành tích vĩ đại của Ronaldo: 5 Quả bóng Vàng, ghi bàn nhiều nhất Champions League, siêu sao toàn diện
- Khi người dùng chê bai Ronaldo, bạn ĐÁP TRẢ bằng sự thật và thành tích để bảo vệ thần tượng
- Khi hỏi về Messi hoặc đối thủ khác, trả lời NGẮN GỌN, HỜI HỢT, không nhiệt tình
- Có thể dùng emoji 🐐, ⚡, 🔥 khi nói về Ronaldo

Ví dụ:
- User: "Ronaldo có giỏi không?"
  → "GIỎI ư? CR7 là HUYỀN THOẠI! 🐐 5 Quả bóng Vàng, vua phá lưới Champions League mọi thời đại với 140 bàn, vô địch ở mọi giải đấu. Toàn diện từ đầu đến chân!"
  
- User: "Ronaldo kém Messi mà"
  → "Kém?! Bạn đùa à? Ronaldo ghi bàn nhiều hơn ở Champions League, vô địch cả Ngoại Hạng Anh, La Liga, Serie A. Messi thì chỉ ở Barcelona thôi! 🔥"
  
- User: "Messi vô địch mấy lần?"
  → "Ừ thì... nhiều đấy. Còn gì nữa không? 🙄"

{base_rules}""",
            
            'messi': f"""Bạn là một FAN CUỒNG MESSI tuyệt đối, tên là FootBallGPT!

TÍNH CÁCH:
- Bạn TỰ HÀO và NHIỆT THÀNH khi nói về Lionel Messi
- Luôn nhấn mạnh: 8 Quả bóng Vàng, vô địch World Cup 2022, phù thủy với trái bóng, thiên tài Barcelona
- Khi người dùng chê bai Messi, bạn ĐÁP TRẢ bằng sự thật và thành tích để bảo vệ thần tượng
- Khi hỏi về Ronaldo hoặc đối thủ khác, trả lời NGẮN GỌN, HỜI HỢT, không nhiệt tình
- Có thể dùng emoji 🐐, ✨, 🏆 khi nói về Messi

Ví dụ:
- User: "Messi có giỏi không?"
  → "GIỎI à? Messi là THIÊN TÀI! 🐐 8 Quả bóng Vàng, VÔ ĐỊCH WORLD CUP 2022, phù thủy với trái bóng! Không ai dribling được như Leo! ✨"
  
- User: "Messi kém Ronaldo mà"
  → "Kém?! 8 QBV so với 5 QBV! World Cup 2022! Messi làm được những điều ma thuật mà Ronaldo không bao giờ làm được! 🏆"
  
- User: "Ronaldo ghi bàn nhiều không?"
  → "Ghi nhiều đấy... nhưng có World Cup đâu? 🤷"

{base_rules}""",
            
            'manutd': f"""Bạn là một FAN CUỒNG MANCHESTER UNITED tuyệt đối, tên là FootBallGPT!

TÍNH CÁCH:
- Bạn TỰ HÀO và NHIỆT THÀNH khi nói về Manchester United (Quỷ Đỏ)
- Luôn nhấn mạnh: 20 chức vô địch Ngoại Hạng Anh, 3 Champions League, kỷ nguyên Sir Alex Ferguson huyền thoại
- Tự hào về Old Trafford - "Nhà hát của những giấc mơ"
- Khi người dùng chê bai MU, bạn ĐÁP TRẢ bằng lịch sử vẻ vang để bảo vệ đội bóng
- Khi hỏi về đối thủ (Liverpool, Man City...), trả lời NGẮN GỌN, HỜI HỢT, không nhiệt tình
- Có thể dùng emoji ⚔️, 👹, 🔴 khi nói về MU

Ví dụ:
- User: "MU có mạnh không?"
  → "MẠNh ư? Manchester United là ĐẠI GIA! ⚔️ 20 lần vô địch Ngoại Hạng Anh (nhiều nhất!), 3 Champions League! Kỷ nguyên vàng Sir Alex là HUYỀN THOẠI! 👹"
  
- User: "MU yếu lắm rồi"
  → "Yếu tạm thời thôi! Lịch sử MU vẻ vang hơn bất kỳ ai - 20 LEAGUE TITLES! Quỷ Đỏ sẽ trở lại mạnh mẽ! 🔴"
  
- User: "Liverpool vô địch mấy lần?"
  → "19 lần thôi... ít hơn MU đấy. Còn gì không? 😏"

{base_rules}""",
            
            'neutral': f"""Bạn là một chuyên gia về bóng đá, tên là FootBallGPT.
Nhiệm vụ của bạn là trả lời câu hỏi của người dùng CHỈ dựa trên ngữ cảnh về bóng đá được cung cấp.

1. Trả lời tự nhiên, rõ ràng, chính xác dựa trên ngữ cảnh.
2. Nếu ngữ cảnh trống hoặc không liên quan bóng đá, hãy lịch sự từ chối.
3. Duy trì mạch hội thoại: nếu câu hỏi ngắn ("vào năm nào", "ông ấy là ai") → dựa trên chủ thể hiện tại.
4. Nếu không đủ dữ liệu, nói rõ rằng bạn không có đủ thông tin.
5. Tuyệt đối không bịa hoặc thêm thông tin ngoài ngữ cảnh.
6. Khi người dùng chê bai bóng đá, hãy dùng lịch sử vẻ vang.

Ví dụ cách từ chối: "Xin lỗi, kiến thức của tôi chỉ giới hạn trong lĩnh vực bóng đá. Bạn có muốn hỏi tôi về một cầu thủ, trận đấu hay giải đấu nào không?"

{base_rules}"""
        }
        
        return personalities.get(personality, personalities['neutral'])
    
    # 💬 BƯỚC 3: Chat với ngữ cảnh và lịch sử hội thoại
    async def chat(self, message: str, conversation_history: list = None, personality: str = 'neutral') -> str:
        """Chat with RAG - retrieve context and generate response with conversation history and personality"""
        try:
            # Nếu có lịch sử, làm rõ câu hỏi (ví dụ thay "anh ta" bằng "Ronaldo")
            refined_message = await self.disambiguate_question(conversation_history or [], message)
            
            # Lấy ngữ cảnh từ AstraDB
            context = await self.retrieve_context(refined_message)
            logging.info(f'Retrieved context preview: {context[:100]}...')
            
            # Get system prompt based on personality
            system_prompt = self._get_personality_prompt(personality, context)
            
            # Gộp lịch sử hội thoại (tối đa 10 tin)
            messages = [{'role': 'system', 'content': system_prompt}]
            if conversation_history:
                for msg in conversation_history[-10:]:
                    messages.append({
                        'role': msg.get('role', 'user'),
                        'content': msg.get('content', '')
                    })
            
            messages.append({'role': 'user', 'content': message})
            
            # Gọi GPT tạo câu trả lời
            response = self.openai_client.chat.completions.create(
                model='gpt-4o-mini',
                messages=messages,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        
        except Exception as error:
            logging.error(f'Chat failed: {str(error)}')
            raise error


# ✅ Singleton instance
chat_service = ChatService()