◎本番用docker起動コマンド

対象ファイル
dockerfile:TestDockerfile
docker-compose.yaml:test-docker-compose.yaml

起動コマンド
docker build -t housework-flask-app .
docker-compose up -d





◎開発用docker起動コマンド

対象ファイル
dockerfile:Dockerfile
docker-compose.yaml:docker-compose.yaml



起動コマンド
cd C:\Docker_app\docker_housework

docker build -t housework-flask-app -f TestDockerfile .
docker-compose -f test-docker-compose.yml up -d