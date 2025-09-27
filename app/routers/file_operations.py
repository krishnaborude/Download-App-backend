import os
import socket
import qrcode
import uuid
from io import BytesIO
from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from fastapi.responses import FileResponse, Response, StreamingResponse
from typing import List, Dict, Optional
import shutil
from datetime import datetime, timedelta

router = APIRouter()

# Store file data with download token and usage tracking
file_storage: Dict[str, Dict] = {}

def generate_download_token() -> str:
    """Generate a unique token for downloads"""
    return str(uuid.uuid4())[:8].upper()


def cleanup_expired_files():
    """
    Remove expired file entries from file_storage and their corresponding files
    """
    now = datetime.now()
    expired_tokens = [token for token, data in file_storage.items() if data.get("expiry_time") and now > data["expiry_time"]]
    
    for token in expired_tokens:
        try:
            file_data = file_storage[token]
            # Clean up all files associated with this token
            if "files" in file_data:
                for file_info in file_data["files"]:
                    try:
                        file_path = file_info["file_path"]
                        if os.path.exists(file_path):
                            os.remove(file_path)
                    except Exception as e:
                        print(f"Error removing file: {str(e)}")
                        
            # Check for potential zip file
            zip_path = os.path.join(UPLOAD_DIR, f"download_{token}.zip")
            if os.path.exists(zip_path):
                try:
                    os.remove(zip_path)
                except Exception as e:
                    print(f"Error removing zip file: {str(e)}")
                    
            # Remove from storage
            del file_storage[token]
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")

async def cleanup_used_file(token: str):
    """
    Clean up files after they have been successfully downloaded
    """
    try:
        if token in file_storage:
            file_data = file_storage[token]
            # Remove all files associated with this token
            if "files" in file_data:
                for file_info in file_data["files"]:
                    try:
                        if os.path.exists(file_info["file_path"]):
                            os.remove(file_info["file_path"])
                    except Exception as e:
                        print(f"Error removing file {file_info['filename']}: {str(e)}")
                
                # Check if there might be a zip file
                zip_path = os.path.join(UPLOAD_DIR, f"download_{token}.zip")
                if os.path.exists(zip_path):
                    try:
                        os.remove(zip_path)
                    except Exception as e:
                        print(f"Error removing zip file: {str(e)}")
            
            # Remove token from storage
            del file_storage[token]
    except Exception as e:
        print(f"Error cleaning up files for token {token}: {str(e)}")


def generate_qr_code(url: str) -> bytes:
    """
    Generate QR code for the given URL
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr

def get_server_url(request: Request) -> str:
    """
    Get the server's network accessible URL
    """
    def get_local_ips():
        ips = []
        try:
            # Try getting IP by connecting to public DNS
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ips.append(s.getsockname()[0])
            s.close()
        except Exception:
            pass

        try:
            # Get all network interface IPs
            hostname = socket.gethostname()
            for ip in socket.gethostbyname_ex(hostname)[2]:
                if not ip.startswith("127."):  # Skip localhost
                    ips.append(ip)
        except Exception:
            pass

        if not ips:  # If no IPs found, fallback to basic method
            try:
                hostname = socket.gethostname()
                ips.append(socket.gethostbyname(hostname))
            except Exception:
                ips.append("127.0.0.1")  # Last resort fallback

        return list(set(ips))  # Remove duplicates

    local_ips = get_local_ips()
    port = request.url.port or 8000  # Fallback to 8000 if port is None
    
    # Print all available IPs for debugging
    print("\nAvailable network URLs:")
    for ip in local_ips:
        print(f"http://{ip}:{port}")
    
    # Use the first non-localhost IP, or localhost if that's all we have
    for ip in local_ips:
        if not ip.startswith("127."):
            return f"http://{ip}:{port}"
    
    return f"http://{local_ips[0]}:{port}"

# Configure upload directory
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router.post("/upload/")
async def upload_file(request: Request, file: UploadFile = File(...)):
    """
    Upload a single file to the server and return a download link with one-time use token
    """
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Generate one-time use token and store file info
        token = generate_download_token()
        expiry_time = datetime.now() + timedelta(minutes=10)  # Token expires in 10 minutes
        file_storage[token] = {
            "files": [{
                "filename": file.filename,
                "file_path": file_path
            }],
            "expiry_time": expiry_time,
            "used": False
        }
        
        # Generate download link using network IP
        base_url = get_server_url(request)
        download_link = f"{base_url}/api/download/{token}"
        qr_code_link = f"{base_url}/api/qr-code/{token}"
        
        # For local testing, also provide localhost URLs
        localhost_base = f"http://127.0.0.1:{request.url.port}"
        localhost_download = f"{localhost_base}/api/download/{token}"
        localhost_qr = f"{localhost_base}/api/qr-code/{token}"
        
        # Clean up expired files
        # cleanup_expired_files()
        
        return {
            "token": token,
            "filename": file.filename,
            "status": "success",
            "download_link": download_link,
            "localhost_download": localhost_download,
            "qr_code_link": qr_code_link,
            "localhost_qr": localhost_qr,
            "message": "link expires in 10 minutes. Use localhost links for local testing."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-multiple/")
async def upload_multiple_files(request: Request, files: List[UploadFile] = File(...)):
    """
    Upload multiple files to the server and store them under a single one-time use token
    """
    try:
        # Generate one token for all files
        token = generate_download_token()
        base_url = get_server_url(request)
        file_list = []
        
        # Process and store all files
        for file in files:
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            file_list.append({
                "filename": file.filename,
                "file_path": file_path
            })
        
        # Store all files under the same token
        expiry_time = datetime.now() + timedelta(minutes=10)  # Token expires in 10 minutes
        file_storage[token] = {
            "files": file_list,
            "expiry_time": expiry_time,
            "used": False
        }
        
        # Generate links for the batch
        download_link = f"{base_url}/api/download/{token}"
        qr_code_link = f"{base_url}/api/qr-code/{token}"
        
        # Create response with all file details
        filenames = [f["filename"] for f in file_list]
        
        # Clean up expired files
        cleanup_expired_files()
        
        return {
            "token": token,
            "filenames": filenames,
            "status": "success",
            "download_link": download_link,
            "qr_code_link": qr_code_link,
            "file_count": len(filenames),
            "message": "link expires in 10 minutes"
        }
    except Exception as e:
        # Clean up any partially uploaded files in case of error
        if token in file_storage:
            file_data = file_storage[token]
            del file_storage[token]
            if "files" in file_data:
                for file_info in file_data["files"]:
                    try:
                        if os.path.exists(file_info["file_path"]):
                            os.remove(file_info["file_path"])
                    except Exception:
                        pass
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{token}")
async def download_file(token: str, request: Request):
    """
    Download files using a one-time download token. For multiple files, creates a zip archive.
    """
    print(f"\nDownload request received for token: {token}")
    print(f"Available tokens: {list(file_storage.keys())}")
    try:
        # Clean up expired files
        cleanup_expired_files()
        print(f"After cleanup, available tokens: {list(file_storage.keys())}")

        # Check if token exists and is valid
        if token not in file_storage:
            print(f"Token {token} not found in storage")
            raise HTTPException(status_code=404, detail="Files not found or link has expired")

        file_data = file_storage[token]
        print(f"File data found: {file_data}")

        # Check if the token has been used
        if file_data["used"]:
            cleanup_used_file(token)
            raise HTTPException(status_code=410, detail="This download link has already been used")
        
        # Get the list of files
        file_list = file_data["files"]
        
        # Check if all files exist
        for file_info in file_list:
            if not os.path.exists(file_info["file_path"]):
                del file_storage[token]
                raise HTTPException(status_code=404, detail="One or more files not found on server")
        
        # For multiple files, create a zip archive
        if len(file_list) > 1:
            zip_filename = f"download_{token}.zip"
            zip_path = os.path.join(UPLOAD_DIR, zip_filename)
            
            import zipfile
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_info in file_list:
                    zipf.write(file_info["file_path"], file_info["filename"])
            
            # Create response with the zip file
            response = FileResponse(
                path=zip_path,
                filename=zip_filename,
                media_type="application/zip"
            )
        else:
            # Single file download
            file_info = file_list[0]
            response = FileResponse(
                path=file_info["file_path"],
                filename=file_info["filename"],
                media_type="application/octet-stream"
            )
        
        # Mark token as used
        file_data["used"] = True
        
        # Set up background task for cleanup
        async def cleanup_files():
            try:
                # Remove all files
                for file_info in file_list:
                    if os.path.exists(file_info["file_path"]):
                        os.remove(file_info["file_path"])
                
                # Remove zip file if it was created
                if len(file_list) > 1 and os.path.exists(zip_path):
                    os.remove(zip_path)
                    
                # Remove token from storage
                del file_storage[token]
            except Exception as e:
                print(f"Error during cleanup: {str(e)}")
        
        response.background = cleanup_files
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/qr-code/{token}")
async def get_qr_code(token: str, request: Request):
    """
    Get QR code for downloading a file using a token
    """
    try:
        # Clean up expired files
        cleanup_expired_files()
        
        # Check if token exists and is valid
        if token not in file_storage:
            raise HTTPException(status_code=404, detail="File not found or link has expired")
        
        file_data = file_storage[token]
        
        # Check if the token has been used
        if file_data["used"]:
            del file_storage[token]
            raise HTTPException(status_code=410, detail="This download link has already been used")
        
        # Check if the file exists
        if not os.path.exists(file_data["file_path"]):
            del file_storage[token]
            raise HTTPException(status_code=404, detail="File not found on server")
        
        # Generate QR code for the download URL
        base_url = get_server_url(request)
        download_url = f"{base_url}/api/download/{token}"
        qr_code = generate_qr_code(download_url)
        
        # Mark the token as used and prepare for cleanup
        file_data["used"] = True
        file_path = file_data["file_path"]
        filename = file_data["filename"]
        
        # Create response first
        response = Response(content=qr_code, media_type="image/png")
        
      
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
