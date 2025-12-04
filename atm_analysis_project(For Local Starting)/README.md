Как запустить (Инструкция)
Убедитесь, что у вас установлен Python (3.9+).
Откройте терминал в папке проекта.
Создайте виртуальное окружение и установите библиотеки:
```
python -m venv venv
# Для Windows:
venv\Scripts\activate
# Для Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```
Запустите анализ:
```
python main.py
```
После завершения в папке data/ появятся файлы:
recommendations.csv (таблица с данными).
map.html (интерактивная карта, которую можно открыть в браузере).
