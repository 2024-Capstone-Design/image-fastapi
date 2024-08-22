# Python 3.9 이미지를 베이스로 사용합니다.
FROM python:3.9-slim

# 작업 디렉토리를 설정합니다.
WORKDIR /app

# 필요한 시스템 라이브러리 설치
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 필요한 파일들을 컨테이너로 복사합니다.
COPY requirements.txt requirements.txt
COPY . .

# 필요한 Python 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# FastAPI 서버를 Gunicorn을 사용해 실행
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8000"]
