# 💻 Tech Stack

### Programming Languages
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![C++](https://img.shields.io/badge/c++-%2300599C.svg?style=for-the-badge&logo=c%2B%2B&logoColor=white)

### AI / Machine Learning
![PyTorch](https://img.shields.io/badge/PyTorch-%23EE4C2C.svg?style=for-the-badge&logo=PyTorch&logoColor=white) ![TensorFlow](https://img.shields.io/badge/TensorFlow-%23FF6F00.svg?style=for-the-badge&logo=TensorFlow&logoColor=white) ![Keras](https://img.shields.io/badge/Keras-%23D00000.svg?style=for-the-badge&logo=Keras&logoColor=white) ![scikit-learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)

### Data Science
![NumPy](https://img.shields.io/badge/numpy-%23013243.svg?style=for-the-badge&logo=numpy&logoColor=white)

### Backend
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)

### Web
![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB) ![Vite](https://img.shields.io/badge/vite-%23646CFF.svg?style=for-the-badge&logo=vite&logoColor=white)

### Deployment
![Vercel](https://img.shields.io/badge/vercel-%23000000.svg?style=for-the-badge&logo=vercel&logoColor=white) ![Render](https://img.shields.io/badge/Render-%46E3B7.svg?style=for-the-badge&logo=render&logoColor=white)

### Databases
![MongoDB](https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=for-the-badge&logo=mongodb&logoColor=white) ![MySQL](https://img.shields.io/badge/mysql-4479A1.svg?style=for-the-badge&logo=mysql&logoColor=white)

### GPU Computing
![CUDA](https://img.shields.io/badge/cuda-000000.svg?style=for-the-badge&logo=nVIDIA&logoColor=green)

---

## Giới thiệu

Đây là dự án chatbot RAG (Retrieval-Augmented Generation) với backend Python (FastAPI), frontend React + Vite, và hỗ trợ ML/AI.

## Cấu trúc ứng dụng

- `api/`: API server
- `client/`: front-end React
- `data/`: scripts tải dữ liệu, ingestion, tạo collection
- `app.py`, `main.py`, `routes.py`: server chính
- `chat_service.py`, `db_service.py`: logic chatbot + DB

## Cách triển khai ứng dụng

1. Cài đặt môi trường
   - `python -m venv venv`
   - Windows: `venv\Scripts\activate`
   - `pip install -r requirements.txt`

2. Chạy backend
   - `uvicorn app:app --reload --host 0.0.0.0 --port 8000`

3. Chạy frontend
   - `cd client`
   - `npm install`
   - `npm run dev`

4. Triển khai trên Vercel hoặc Render
   - Kết nối repository
   - Cấu hình biến môi trường (ví dụ: `OPENAI_API_KEY`, `MONGO_URI` ...)
   - Thiết lập build command:
     - backend: `python -m uvicorn app:app --host 0.0.0.0 --port 8000`
     - frontend: `npm run build` (trong folder `client`)

## Lưu ý

- Tùy chỉnh `requirements.txt` và `package.json` cho đúng phiên bản.
- Đảm bảo `data/` đã được nạp và index nếu dùng vector DB.
- Kiểm tra cấu hình bảo mật và giới hạn API key khi deploy.
