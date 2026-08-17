#!/usr/bin/env python3
"""
PDF Unlocker & Security API (FastAPI)
=====================================
A high-performance RESTful microservice for PDF decryption, permissions removal,
and security inspection. Designed for deployment and monetization on RapidAPI.

Author: Antigravity Pair Programmer
License: MIT
"""

import os
import io
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, Header, HTTPException, status
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import pikepdf

app = FastAPI(
    title="PDF Unlocker & Security API",
    description="Professional REST API to inspect PDF security attributes and remove encryption/passwords.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for cross-origin web requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Optional RapidAPI Proxy Secret Validation
RAPIDAPI_SECRET = os.getenv("RAPIDAPI_PROXY_SECRET", None)


def verify_rapidapi_secret(x_rapidapi_proxy_secret: Optional[str] = Header(None)):
    """Enforce request origination from RapidAPI if secret is configured."""
    if RAPIDAPI_SECRET and x_rapidapi_proxy_secret != RAPIDAPI_SECRET:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Direct API access is disabled. Please route requests via RapidAPI."
        )


@app.get("/", tags=["General"])
async def root():
    return {
        "service": "PDF Unlocker & Security API",
        "version": "1.0.0",
        "status": "online",
        "documentation": "/docs"
    }


@app.get("/health", tags=["General"])
async def health_check():
    return {"status": "healthy"}


@app.post(
    "/api/v1/inspect",
    tags=["PDF Operations"],
    summary="Inspect PDF Security & Permissions",
    description="Upload a PDF file to retrieve detailed security, encryption, and permission properties."
)
async def inspect_pdf(
    file: UploadFile = File(..., description="Target PDF file to inspect"),
    password: Optional[str] = Form(None, description="Optional user password if required to open"),
    x_rapidapi_proxy_secret: Optional[str] = Header(None)
):
    verify_rapidapi_secret(x_rapidapi_proxy_secret)

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. File must be a PDF document."
        )

    try:
        content = await file.read()
        pdf_stream = io.BytesIO(content)

        with pikepdf.open(pdf_stream, password=password or "") as pdf:
            meta_dict = {}
            try:
                with pdf.open_metadata() as meta:
                    meta_dict = {
                        "title": meta.get("dc:title", "N/A"),
                        "author": meta.get("dc:creator", "N/A"),
                        "subject": meta.get("dc:description", "N/A"),
                        "producer": meta.get("pdf:Producer", "N/A"),
                        "creation_date": meta.get("xmp:CreateDate", "N/A"),
                    }
            except Exception:
                meta_dict = {"note": "Metadata unreadable or unavailable"}

            permissions = {
                "allow_printing": getattr(pdf.allow, "accessibility", True) or getattr(pdf.allow, "modify_assembly", True),
                "allow_copying": getattr(pdf.allow, "accessibility", True) or getattr(pdf.allow, "extract", True),
                "allow_modifying": getattr(pdf.allow, "modify_contents", True) or getattr(pdf.allow, "modify_annotation", True),
            }

            return JSONResponse(content={
                "filename": file.filename,
                "size_bytes": len(content),
                "page_count": len(pdf.pages),
                "is_encrypted": pdf.is_encrypted,
                "metadata": meta_dict,
                "permissions": permissions
            })

    except pikepdf.PasswordError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "filename": file.filename,
                "is_encrypted": True,
                "requires_password": True,
                "error": "Password required to access PDF content."
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to inspect PDF: {str(e)}"
        )


@app.post(
    "/api/v1/unlock",
    tags=["PDF Operations"],
    summary="Unlock / Decrypt PDF File",
    description="Upload an encrypted or restricted PDF file to receive a decrypted, unrestricted PDF file."
)
async def unlock_pdf(
    file: UploadFile = File(..., description="Target PDF file to unlock"),
    password: Optional[str] = Form(None, description="Password required to open encrypted PDF (if applicable)"),
    x_rapidapi_proxy_secret: Optional[str] = Header(None)
):
    verify_rapidapi_secret(x_rapidapi_proxy_secret)

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. File must be a PDF document."
        )

    try:
        content = await file.read()
        pdf_in = io.BytesIO(content)
        pdf_out = io.BytesIO()

        with pikepdf.open(pdf_in, password=password or "") as pdf:
            pdf.save(pdf_out)

        pdf_out.seek(0)
        output_filename = f"unlocked_{file.filename}"

        return StreamingResponse(
            pdf_out,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=\"{output_filename}\""
            }
        )

    except pikepdf.PasswordError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect or missing password required to unlock this PDF."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process PDF file: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
