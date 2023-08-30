# 使用 Python 3.11.4 作為基礎映像
FROM python:3.11.4-slim

# 設定工作目錄
WORKDIR /app

# 複製 requirements.txt 檔案到容器中的 /app 目錄
COPY requirements.txt /app

# 安裝 requirements.txt 中的套件
RUN pip install --no-cache-dir -r requirements.txt