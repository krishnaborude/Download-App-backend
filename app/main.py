from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import file_operations

app = FastAPI(title="File Upload/Download API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(file_operations.router, prefix="/api", tags=["files"])

if __name__ == "__main__":
    import uvicorn
    import socket
    
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    port = 8000
    
    print(f"\nServer is accessible at:")
    print(f"Local machine: http://localhost:{port}")
    print(f"Other devices on network: http://{local_ip}:{port}")
    print("\nShare the network URL with other devices to allow file downloads\n")
    
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)