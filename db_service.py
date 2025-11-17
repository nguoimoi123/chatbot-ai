import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime
import logging


load_dotenv()

# Singleton pattern for the database client
_mongo_client = None
_db = None

def get_db():
    """Lấy kết nối đến database MongoDB."""
    global _mongo_client, _db
    if _db is None:
        mongo_uri = os.environ.get("MONGODB_URI", "").strip()
        if not mongo_uri:
            raise Exception("MONGODB_URI not set in environment variables.")
        
        _mongo_client = MongoClient(mongo_uri)
        db_name = os.environ.get("MONGODB_DATABASE", "football_gpt_auth")
        _db = _mongo_client[db_name]
        logging.info(f"Connected to MongoDB database: {db_name}")
    return _db

# --- User Operations ---
def find_user_by_id(user_id: str):
    """Tìm user theo ID."""
    db = get_db()
    return db.users.find_one({"_id": user_id})

# --- OAuth Operations ---
def find_oauth_token(user_id: str, browser_session_key: str, provider: str):
    """Tìm token OAuth."""
    db = get_db()
    doc = db.oauth.find_one({
        "user_id": user_id,
        "browser_session_key": browser_session_key,
        "provider": provider
    })
    return doc['token'] if doc else None

def save_oauth_token(user_id: str, browser_session_key: str, provider: str, token: dict):
    """Lưu token OAuth."""
    db = get_db()
    db.oauth.delete_many({
        "user_id": user_id,
        "browser_session_key": browser_session_key,
        "provider": provider
    })
    db.oauth.insert_one({
        "user_id": user_id,
        "browser_session_key": browser_session_key,
        "provider": provider,
        "token": token
    })

def delete_oauth_token(user_id: str, browser_session_key: str, provider: str):
    """Xóa token OAuth."""
    db = get_db()
    db.oauth.delete_many({
        "user_id": user_id,
        "browser_session_key": browser_session_key,
        "provider": provider
    })

# --- Conversation Operations ---
def create_conversation(user_id: str, title: str = "New Chat"):
    """Tạo một conversation mới."""
    db = get_db()
    result = db.conversations.insert_one({
        "user_id": user_id,
        "title": title,
        "messages": [],
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    })
    return str(result.inserted_id)

def get_conversations(user_id: str, limit: int = 50):
    """Lấy danh sách conversations của user."""
    db = get_db()
    conversations = db.conversations.find(
        {"user_id": user_id}
    ).sort("updated_at", -1).limit(limit)
    return [
        {
            "id": str(c["_id"]),
            "title": c.get("title", "New Chat"),
            "created_at": c["created_at"].isoformat(),
            "updated_at": c["updated_at"].isoformat(),
            "message_count": len(c.get("messages", []))
        } for c in conversations
    ]

def get_conversation(conversation_id: str, user_id: str = None):
    """Lấy chi tiết một conversation. Nếu user_id được cung cấp, verify ownership."""
    from bson.objectid import ObjectId
    db = get_db()
    
    try:
        obj_id = ObjectId(conversation_id)
    except:
        return None
    
    query = {"_id": obj_id}
    if user_id:
        query["user_id"] = user_id
    
    conv = db.conversations.find_one(query)
    if not conv:
        return None
    return {
        "id": str(conv["_id"]),
        "title": conv.get("title", "New Chat"),
        "messages": conv.get("messages", []),
        "created_at": conv["created_at"].isoformat(),
        "updated_at": conv["updated_at"].isoformat()
    }

def add_message_to_conversation(conversation_id: str, role: str, content: str, user_id: str = None):
    """Thêm tin nhắn vào conversation. Nếu user_id được cung cấp, verify ownership."""
    from bson.objectid import ObjectId
    db = get_db()
    
    try:
        obj_id = ObjectId(conversation_id)
    except:
        return False
    
    query = {"_id": obj_id}
    if user_id:
        query["user_id"] = user_id
    
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    }
    result = db.conversations.update_one(
        query,
        {
            "$push": {"messages": message},
            "$set": {"updated_at": datetime.now()}
        }
    )
    return result.modified_count > 0

def update_conversation_title(conversation_id: str, title: str, user_id: str = None):
    """Cập nhật title của conversation. Nếu user_id được cung cấp, verify ownership."""
    from bson.objectid import ObjectId
    db = get_db()
    
    try:
        obj_id = ObjectId(conversation_id)
    except:
        return False
    
    query = {"_id": obj_id}
    if user_id:
        query["user_id"] = user_id
    
    result = db.conversations.update_one(
        query,
        {"$set": {"title": title, "updated_at": datetime.now()}}
    )
    return result.modified_count > 0

def delete_conversation(conversation_id: str, user_id: str = None):
    """Xóa một conversation. Nếu user_id được cung cấp, verify ownership."""
    from bson.objectid import ObjectId
    db = get_db()
    
    try:
        obj_id = ObjectId(conversation_id)
    except:
        return False
    
    query = {"_id": obj_id}
    if user_id:
        query["user_id"] = user_id
    
    result = db.conversations.delete_one(query)
    return result.deleted_count > 0

# --- Legacy Chat History Operations (kept for backwards compatibility) ---
def save_chat_history(user_id: str, message: str, reply: str):
    """Lưu một tin nhắn vào lịch sử chat (deprecated - use conversations instead)."""
    db = get_db()
    db.chat_histories.insert_one({
        "user_id": user_id,
        "message": message,
        "reply": reply,
        "created_at": datetime.now()
    })

def get_chat_history(user_id: str, limit: int = 50):
    """Lấy lịch sử chat của một user (deprecated - use conversations instead)."""
    db = get_db()
    histories = db.chat_histories.find(
        {"user_id": user_id}
    ).sort("created_at", -1).limit(limit)
    return [
        {
            "id": str(h["_id"]),
            "message": h["message"],
            "reply": h["reply"],
            "created_at": h["created_at"].isoformat()
        } for h in histories
    ]

class User:
    """Đây là class User để flask-login hoạt động với dữ liệu từ MongoDB."""
    def __init__(self, user_dict):
        self._dict = user_dict
        for key, value in user_dict.items():
            setattr(self, key, value)
        # Đảm bảo có thuộc tính 'id' cho flask-login
        self.id = self._dict.get('_id')

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

# --- User Operations (thêm hàm mới) ---
def find_user_by_email(email: str):
    """Tìm user theo email."""
    db = get_db()
    user_data = db.users.find_one({"email": email})
    return User(user_data) if user_data else None

# --- Cập nhật lại hàm save_user để trả về User object ---
def save_user(user_claims: dict):
    """Lưu hoặc cập nhật thông tin user và trả về User object."""
    db = get_db()
    user_data = {
        "_id": user_claims.get('sub') or str(user_claims.get('id')), # Dùng sub của Google hoặc id của GitHub
        "email": user_claims.get('email'),
        "first_name": user_claims.get('given_name') or user_claims.get('name'),
        "last_name": user_claims.get('family_name'),
        "profile_image_url": user_claims.get('picture') or user_claims.get('avatar_url'),
        "updated_at": datetime.now()
    }
    # Dùng upsert để tạo mới nếu chưa có, hoặc cập nhật nếu đã tồn tại
    db.users.update_one(
        {"_id": user_data["_id"]},
        {"$set": user_data, "$setOnInsert": {"created_at": datetime.now()}},
        upsert=True
    )
    # Trả về User object
    return User(find_user_by_id(user_data["_id"]))