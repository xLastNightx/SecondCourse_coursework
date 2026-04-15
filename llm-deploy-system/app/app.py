from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from openai import OpenAI
import os

# --- НАСТРОЙКИ OPENROUTER ---
# Используем переменную окружения для ключа (безопасно)
YOUR_OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', '')
# Если переменная окружения не установлена, вставь ключ сюда временно:
# YOUR_OPENROUTER_API_KEY = "sk-or-v1-..."

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=YOUR_OPENROUTER_API_KEY,
)

class Handler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            html = '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>LLM Text Generator</title>
                <style>
                    body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
                    textarea { width: 100%; height: 100px; margin: 10px 0; }
                    button { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }
                    button:hover { background: #0056b3; }
                    #result { margin-top: 20px; padding: 10px; background: #f0f0f0; border-radius: 5px; white-space: pre-wrap; }
                </style>
            </head>
            <body>
                <h1>LLM Text Generator</h1>
                <p>Введите промпт, и нейросеть сгенерирует текст:</p>
                <textarea id="prompt" placeholder="Например: Напиши частушку про кота"></textarea>
                <br>
                <button onclick="generate()">Сгенерировать</button>
                <div id="result"></div>
                
                <script>
                    async function generate() {
                        const prompt = document.getElementById('prompt').value;
                        const resultDiv = document.getElementById('result');
                        resultDiv.innerHTML = 'Генерация...';
                        
                        try {
                            const response = await fetch('/generate', {
                                method: 'POST',
                                headers: {'Content-Type': 'application/json'},
                                body: JSON.stringify({prompt: prompt})
                            });
                            const data = await response.json();
                            resultDiv.innerHTML = '<strong>Результат:</strong><br>' + data.response;
                        } catch(error) {
                            resultDiv.innerHTML = 'Ошибка: ' + error;
                        }
                    }
                </script>
            </body>
            </html>
            '''
            self.wfile.write(html.encode('utf-8'))
            
        elif self.path == '/health':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/generate':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            prompt = data.get('prompt', '')

            try:
                # Используем одну из проверенных бесплатных моделей
                completion = client.chat.completions.create(
                    model="arcee-ai/trinity-large-preview:free",  # <-- ЗДЕСЬ МЕНЯЙ МОДЕЛЬ
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=200,
                    temperature=0.7,
                )
                generated_text = completion.choices[0].message.content
                response_data = {'response': generated_text}

            except Exception as e:
                response_data = {'response': f'Ошибка: {str(e)}', 'error': True}

            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    port = 8000
    server = HTTPServer(('0.0.0.0', port), Handler)
    print(f'LLM генератор запущен на порту {port}')
    print(f'Открой в браузере: http://localhost:{port}')
    server.serve_forever()