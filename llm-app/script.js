// Отправка запроса по клавише Enter (Shift+Enter — перенос строки)
document.getElementById('prompt').addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();  // Чтобы не добавлялся перенос строки
        ask();               // Вызов функции отправки
    }
});

// Основная функция: отправка промпта на сервер и отображение ответа
async function ask() {
    const prompt = document.getElementById('prompt').value;
    const resultDiv = document.getElementById('result');

    // Показываем индикатор загрузки
    resultDiv.innerHTML = 'Думаю...';

    try {
        // POST-запрос к серверу с промптом в формате JSON
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({prompt: prompt})
        });

        // Разбираем JSON-ответ от сервера
        const data = await response.json();

        // Показываем результат или ошибку
        if (data.error) {
            resultDiv.innerHTML = ' X ' + data.response;
        } else {
            resultDiv.innerHTML = '<strong>Ответ ассистента:</strong><br><br>' + data.response;
        }
    } catch (error) {
        // Ошибка сети или сервер недоступен
        resultDiv.innerHTML = 'Ошибка соединения: ' + error;
    }
}