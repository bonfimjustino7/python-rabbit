# Python Rabbit Pub/Sub

- Transferencia de dados utilizando
- Consumidor websocket conectado a uma fila
- Enviando dados de um publicador para consumidores interessados

# Executar

```gunicorn web:main --bind localhost:8080 --worker-class aiohttp.GunicornWebWorker```
