from fastapi import FastAPI, HTTPException
from models import ImageRequest
from image_processor import process_and_upload_images

app = FastAPI()

@app.post("/process_images/")
async def process_images(request: ImageRequest):
    try:
        result = process_and_upload_images(request.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# FastAPI 서버 실행
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
