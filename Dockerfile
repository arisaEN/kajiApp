# ベースイメージとしてPython 3.12.3の軽量バージョンを使用
FROM python:3.9-slim

# 作業ディレクトリを作成
WORKDIR /app



# Pipを最新バージョンにアップデート
RUN pip install --upgrade pip

# requirements.txtをコンテナにコピー
COPY requirements.txt .

# 必要なPythonパッケージをインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションファイルをすべてコンテナにコピー
COPY . .

# 環境変数の設定
ENV FLASK_APP=flaskr
ENV FLASK_ENV=development

# ポート5000を公開
EXPOSE 5000

# アプリを起動
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000", "--debug"]
