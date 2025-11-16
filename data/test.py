import os
from astrapy import DataAPIClient
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()

# Lấy thông tin Astra DB
token = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
endpoint = os.getenv("ASTRA_DB_ENDPOINT")
collection_name = os.getenv("ASTRA_DB_COLLECTION")

# Kiểm tra biến môi trường có đọc được không
if not token or not endpoint:
    raise ValueError("❌ Không đọc được thông tin Astra DB từ file .env")

# Kết nối tới Astra DB
client = DataAPIClient(token)
db = client.get_database(endpoint)
collection = db.get_collection(collection_name)

print("✅ Kết nối Astra DB thành công!")
print("Collection:", collection.name)  # ← sửa dòng này

# Kiểm tra thử xem có collection nào khác không
print("Danh sách collection trong DB:")
for col in db.list_collections():
    print(" -", col["name"])
