from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from openai import OpenAI
import sys
import os

# ОТКЛЮЧЕНИЕ СИСТЕМНОГО ПРОКСИ

# На некоторых компьютерах настроен HTTP-прокси (VPN, корпоративная сеть). Библиотека httpx (внутри openai) пытается пропускать через него даже
# запросы к localhost — и они ломаются. Эти строки принудительно отключают прокси для локальных адресов.
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''

# ПОДКЛЮЧЕНИЕ К LM STUDIO
# LM Studio запускает OpenAI-совместимый API на порту 1234.
# Никаких ключей не нужно — сервер работает только локально.
LMSTUDIO_URL = "http://localhost:1234/v1"

print(f"Подключаюсь к локальному ИИ-серверу: {LMSTUDIO_URL}")

try:
    # Создаём клиент для общения с LM Studio
    client = OpenAI(
        base_url=LMSTUDIO_URL,
        api_key="not-needed"  # Локальному серверу ключ не нужен
    )

    # Получаем список загруженных моделей и берём первую (в LM Studio обычно одна активная модель)
    models = client.models.list()
    MODEL_NAME = models.data[0].id
    print(f"ИИ-ассистент готов. Модель: {MODEL_NAME}")

except Exception as e:
    # Если сервер LM Studio не запущен — выводим инструкцию проверки
    print(f"Ошибка подключения к LM Studio: {e}")
    print("   Проверь:")
    print("   1. LM Studio запущена")
    print("   2. Нужная модель загружена (вкладка Models)")
    print("   3. Сервер активен: вкладка Developer → Start Server")
    print("   4. Сервер работает на порту 1234")
    sys.exit(1)  # Завершение программы

# ВЕБ-СЕРВЕР (обработчик HTTP-запросов)
class Handler(BaseHTTPRequestHandler):
    """
    Обрабатывает входящие запросы от браузера.
    GET  /          — отдаёт HTML-страницу с интерфейсом ассистента
    GET  /style.css — отдаёт файл стилей
    GET  /health    — проверка работоспособности сервера
    POST /generate  — принимает промпт, возвращает ответ нейросети
    """

    def do_GET(self):
        """Обрабатывает GET-запросы: главная страница, стили, проверка здоровья"""

        if self.path == '/':
            # Отдаём HTML-интерфейс ассистента
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            with open('llm-app/index.html', 'r', encoding='utf-8') as f:
                self.wfile.write(f.read().encode('utf-8'))

        elif self.path == '/style.css':
            # Отдаём файл стилей
            self.send_response(200)
            self.send_header('Content-type', 'text/css; charset=utf-8')
            self.end_headers()
            with open('llm-app/style.css', 'r', encoding='utf-8') as f:
                self.wfile.write(f.read().encode('utf-8'))

        elif self.path == '/health':
            # Эндпоинт для проверки, жив ли сервер
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')

        else:
            # Всё остальное — 404
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        """Обрабатывает POST-запросы: генерация ответа от нейросети"""

        if self.path == '/generate':
            # Читаем тело запроса
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            prompt = data.get('prompt', '')

            # Проверяем, что промпт не пустой
            if not prompt.strip():
                response_data = {
                    'response': 'Введите ваш вопрос',
                    'error': True
                }
            else:
                try:
                    # Отправляем запрос к нейросети через LM Studio
                    completion = client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=[
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=200,   # Максимальная длина ответа
                        temperature=0.8,  # Креативность (0 — сухо, 1 — творчески)
                    )
                    # Извлекаем текст ответа
                    generated_text = completion.choices[0].message.content
                    response_data = {'response': generated_text}

                except Exception as e:
                    # Если нейросеть вернула ошибку — показываем её
                    response_data = {
                        'response': f'Ошибка генерации: {str(e)}',
                        'error': True
                    }

            # Отправляем JSON-ответ обратно в браузер
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(
                json.dumps(response_data, ensure_ascii=False).encode('utf-8')
            )

        else:
            # Неизвестный POST-запрос
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    PORT = 8000  # Порт, на котором будет доступен веб-интерфейс

    # Создаём HTTP-сервер:
    server = HTTPServer(('0.0.0.0', PORT), Handler)

    print(f'\nЛокальный ИИ-ассистент запущен: http://localhost:{PORT}')
    print('   Для остановки нажми Ctrl+C')

    # Запускаем бесконечный цикл обработки запросов
    server.serve_forever()