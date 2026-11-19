import os
import secrets
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
import core

app = FastAPI(title="ARABI VPS Manager", version="2.0.0")

def authorize(value):
    expected = os.getenv("API_KEY", "")
    if not expected or not secrets.compare_digest(value or "", expected):
        raise HTTPException(status_code=401, detail="Invalid API key")

class CreateRequest(BaseModel):
    name: str
    ram_mb: int = Field(ge=512, le=262144)
    vcpus: int = Field(ge=1, le=64)
    disk_gb: int = Field(ge=5, le=2048)
    iso: str

@app.get("/")
def index():
    return {"name": "ARABI VPS Manager", "version": "2.0.0", "status": "online"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/host")
def host(x_api_key: str = Header(default="")):
    authorize(x_api_key)
    try:
        return core.host_info()
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.get("/vms")
def vms(x_api_key: str = Header(default="")):
    authorize(x_api_key)
    try:
        return core.list_vms()
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.post("/vms")
def create(body: CreateRequest, x_api_key: str = Header(default="")):
    authorize(x_api_key)
    try:
        return core.create_vm(**body.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/vms/{name}/{action}")
def action(name: str, action: str, x_api_key: str = Header(default="")):
    authorize(x_api_key)
    try:
        return {"result": core.vm_action(name, action)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/vms/{name}")
def delete(name: str, x_api_key: str = Header(default="")):
    authorize(x_api_key)
    try:
        return {"result": core.delete_vm(name),
                "note": "VM definition removed; disk storage preserved."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
