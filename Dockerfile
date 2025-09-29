FROM python:3.11-alpine

# Definir o Python como UNBUFFERED
ENV PYTHONUNBUFFERED=1

# Criando o diretório de trabalho
WORKDIR /app

# Copiar arquivo de requirements.txt
COPY requirements.txt ./

# Instalando as bibliotecas necessárias para aplicação
RUN pip install --no-cache-dir -r requirements.txt

# Expor a porta em que a aplicação Gunicorn irá rodar
EXPOSE 8009

# Comando executado ao iniciar o container
CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0", "--port=8012"]

# Sugestão de comando para criar a imagem
# docker build --tag api-rastreamento-v1.2-image .

# Sugestão de comando para criar o container
# docker run -p 8009:8009 --name api-rastreamento-v1.2-container -v .:/app -v /cte:/cte -d api-rastreamento-v1.2-image

# Sugestão de comando para acessar o container
# docker exec -it api-rastreamento-v1.2-container /bin/sh
