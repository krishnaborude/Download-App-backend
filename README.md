# 🚀 FastAPI File Storage Service

A powerful and secure file storage service built with FastAPI that provides one-time download links and QR codes for easy file sharing.

## ✨ Features

### 🔒 Secure One-Time Downloads
- **Single-Use Links**: Each download link can only be used once
- **Auto-Expiring**: Links automatically expire after 10 minutes
- **Auto-Cleanup**: Files are automatically removed after download
- **Token-Based**: Secure random tokens for file access

### 📦 File Management
- **Single File Upload**: Upload individual files securely
- **Batch Upload**: Upload multiple files at once
- **ZIP Archive**: Automatically creates ZIP archives for multiple files
- **QR Code Generation**: Get QR codes for easy mobile access

### 🛠️ API Endpoints

#### Upload Endpoints
```http
POST /api/upload/
POST /api/upload-multiple/
```

#### Download Endpoints
```http
GET /api/download/{token}
GET /api/qr-code/{token}
```

## 🚀 Getting Started

### Prerequisites
- Python 3.7+
- FastAPI
- uvicorn

### Installation
1. Clone the repository
```bash
git clone Download-App-backend
cd Download-App-backend
```

2. Create a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run the server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📖 API Usage Guide

### Single File Upload
```python
import requests

url = "http://127.0.0.1:8000/api/upload/"
files = {"file": open("example.txt", "rb")}
response = requests.post(url, files=files)

print(response.json())
# Response:
{
    "token": "ABCD1234",
    "filename": "example.txt",
    "status": "success",
    "download_link": "http://127.0.0.1:8000/api/download/ABCD1234",
    "qr_code_link": "http://127.0.0.1:8000/api/qr-code/ABCD1234",
    "message": "link expires in 10 minutes"
}
```

### Multiple File Upload
```python
url = "http://127.0.0.1:8000/api/upload-multiple/"
files = [
    ("files", open("file1.txt", "rb")),
    ("files", open("file2.pdf", "rb"))
]
response = requests.post(url, files=files)

print(response.json())
# Response:
{
    "token": "XYZ98765",
    "filenames": ["file1.txt", "file2.pdf"],
    "status": "success",
    "download_link": "http://127.0.0.1:8000/api/download/XYZ98765",
    "qr_code_link": "http://127.0.0.1:8000/api/qr-code/XYZ98765",
    "file_count": 2,
    "message": "link expires in 10 minutes"
}
```

## 🔒 Security Features

1. **One-Time Downloads**
   - Links become invalid after first use
   - Files are automatically deleted after download

2. **Expiration System**
   - All links expire after 10 minutes
   - Automatic cleanup of expired files

3. **Token System**
   - Secure random tokens for file access
   - No direct file path exposure

## 🌟 Advanced Features

### QR Code Generation
- Each download link gets a corresponding QR code
- Perfect for mobile device access
- Scan to download instantly

### Batch Processing
- Upload multiple files at once
- Automatic ZIP archive creation
- Single download link for multiple files

### File Management
- Automatic file cleanup
- Expired file removal
- Storage optimization

## 📝 API Response Formats

### Success Response
```json
{
    "token": "ABCD1234",
    "filename": "example.txt",
    "status": "success",
    "download_link": "http://127.0.0.1:8000/api/download/ABCD1234",
    "qr_code_link": "http://127.0.0.1:8000/api/qr-code/ABCD1234",
    "message": "link expires in 10 minutes"
}
```

### Error Responses
```json
{
    "detail": "File not found or link has expired"
}
```
```json
{
    "detail": "This download link has already been used"
}
```

## 🛠️ Development

### Running Tests
```bash
pytest
```

### Development Server
```bash
uvicorn app.main:app --reload
```

### API Documentation
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## 📈 Future Enhancements

- [ ] File encryption at rest
- [ ] Custom expiration times
- [ ] Download progress tracking
- [ ] File type validation
- [ ] Maximum file size configuration
- [ ] User authentication system
- [ ] Download statistics
- [ ] Email notifications

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 💖 Support

Give a ⭐️ if this project helped you!