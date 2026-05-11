# Локальный ИИ-ассистент
## Веб-приложение для общения с нейросетью через LM Studio.
## Работает полностью офлайн — без интернета и API-ключей.

Структура проекта:
<pre><code>
SecondCourse_coursework
├──llm-app/
│    ├── app.py          (само приложение)  
|    ├── index.html
|    ├── style.css
│    └── requirements.txt    (зависимости Python)
├──venv
├──requirements.txt
└── README.md           (уже есть)    
</code></pre>

Чтобы запустить проект, надо: 
### 1. Установить Python 3.11, LM Studio
### 2. Включить виртуальное окружение: cd E:\Coursework\SecondCourse_coursework\     
### 3. venv/scripts/activate
### 4. Установить зависимости и библиоткеи: pip install -r requirements.txt
### 5. Загрузить модель (например, Gemma 2 9B) в LM Studio. Убедиться, что модель загружена (вкладка Models, статус READY). Перейти в Developer и изменить статус на Running. Дождаться: [INFO] | [LM STUDIO SERVER] Success! HTTP server listening on port 1234. Проверить браузер: http://localhost:1234/v1/models — должен вернуть JSON.
### 6. python llm-app/app.py 
### 7. Перейти на сайт http://localhost:8000/
(чтобы прервать работу LLM-генератора нажмите CTRL+C)