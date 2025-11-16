# create_collection.py
import os
from astrapy import DataAPIClient
from dotenv import load_dotenv

# Load file .env
load_dotenv()

# Lấy biến môi trường
token = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
endpoint = os.getenv("ASTRA_DB_ENDPOINT")
collection_name = os.getenv("ASTRA_DB_COLLECTION")

if not token or not endpoint or not collection_name:
    raise ValueError("❌ Thiếu thông tin trong file .env (token, endpoint hoặc collection_name)")

# Kết nối Astra
client = DataAPIClient(token)
db = client.get_database(endpoint)

def create_collection_if_not_exists():
    try:
        existing_collections = [col["name"] for col in db.list_collections()]
        if collection_name in existing_collections:
            print(f"✅ Collection '{collection_name}' đã tồn tại.")
        else:
            # ⚙️ Định nghĩa chuẩn vector 1536 chiều
            db.create_collection(
                collection_name,
                definition={
                    "vector": {
                        "dimension": 1536,
                        "metric": "cosine"
                    }
                }
            )
            print(f"✅ Đã tạo collection '{collection_name}' thành công!")

        print("\n📂 Danh sách collection hiện có:")
        for col in db.list_collections():
            print(" -", col["name"])

    except Exception as e:
        print("❌ Lỗi khi tạo hoặc kiểm tra collection:", e)

if __name__ == "__main__":
    print("🔗 Đang kết nối tới Astra DB...")
    create_collection_if_not_exists()
