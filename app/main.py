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
    
    def get_network_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            hostname = socket.gethostname()
            return socket.gethostbyname(hostname)
    
    port = 8000
    network_ip = get_network_ip()
    
    print(f"\nServer is accessible at:")
    print(f"Local testing: http://127.0.0.1:{port}")
    print(f"Local machine: http://localhost:{port}")
    print(f"Other devices on network: http://{network_ip}:{port}")
    print(f"\nAPI Documentation:")
    print(f"Swagger UI: http://{network_ip}:{port}/docs")
    print(f"ReDoc: http://{network_ip}:{port}/redoc")
    print("\nMake sure other devices are on the same network to access the URLs")
    print("If the network IP doesn't work, check your firewall settings\n")
    
    # Ensure we're binding to all interfaces and the port is accessible
    print("\nBinding to all network interfaces (0.0.0.0)...")
    print("If you can't connect from other devices, please check:")
    print("1. Windows Defender Firewall - allow Python/uvicorn through")
    print("2. Antivirus software - allow the connection")
    print("3. Router/network settings - ensure local network access is allowed\n")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",  # Bind to all interfaces
        port=port,
        reload=True,
        access_log=True  # Enable access logging
    )