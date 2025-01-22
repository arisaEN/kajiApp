FROM python:3.9-slim

WORKDIR /app

# 必要なパッケージをインストール
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# Gunicornを使用してアプリケーションを起動
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "flaskr:app"]