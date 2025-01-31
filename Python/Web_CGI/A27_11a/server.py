""" Створюємо локальний веб-сервер.
Для того щоб зайти на нього потрібно запустити цей файл і
перейти у веб-браузері за такою адресою:
localhost:8000
або за явною IP адресою
127.0.0.1:8000
"""

# Знаходиться у головній директорії
from http.server import HTTPServer, CGIHTTPRequestHandler

HOST = ""
PORT = 8000

if __name__ == '__main__':
    print("=== Local webserver ===")
    HTTPServer((HOST, PORT), CGIHTTPRequestHandler).serve_forever()