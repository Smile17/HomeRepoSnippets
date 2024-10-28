""" [B]27.11.
Скласти програму, яка працює в оточенні веб-сервера, для розв’язання задачі.
Знайти у даному рядку символ та довжину найдовшої послідовності однакових
символів, що йдуть підряд.
Для введення рядка використати одне поле введення на сторінці.
Показати рядок на окремій сторінці, виділивши знайдену найдовшу послідовність
іншим кольором.
b) використати WSGI
"""

import cgi
from string import Template


def search_char(string, char):
    """ Повертає індекс початку і довжину найдовшого ланцюжка заданої літери
    """
    idx_m, n = 0, 0
    idx_res, n_res = 0, 0 # змінні для результату
    b = False # параметр, який показує чи ми в підрядку з даною літерею
    for i in range(len(string)):
        if string[i] == char:
            if not b: # якщо підрядок ще не знаходили, то тепер його початок знайдений,
                # відповідно зберігаємо початок і той факт, що ми знайшли початок
                idx_m = i
                b = True
                n = 1
            else:
                n = n + 1 # ми всеердині рядка, накопичуємо результат
        else:
            if n_res < n: # зберігаємо серед них найбільший
                idx_res = idx_m
                n_res = n
            idx_m, n = 0, 0
            b = False # шуканий підрядок скиндається, адже черговий символ ж непідходящим символом

    return idx_res, n_res

def format_string(string, char, idx_res, n_res):
    '''
    Формує HTML рядок, в якому всі шукані літери будуть червоні,а найбільший рядок буде червоним текстом і з жовтим фоном
    '''
    result = ''
    i = 0
    while i < len(string):
        if i == idx_res: # якщо це наш найдовший підрядок, то записуємо його виділяючи кольором текст і фон
            result = result + f"<span style=\"background:yellow;color:red;\">{char * n_res}</span>"
            i = i + n_res
        else:
            if string[i] == char: # інакше виділяємо лише кольором
                result = result + f"<span style=\"color:red;\">{char}</span>"
            else: # всі інші сиволи без змін
                result = result + string[i]
        i = i + 1
    return result


def application(environ, start_response):
    """ Функція веб-сервера обробки запитів веб-клієнта.
    :param environ: словник параметрів, які клієнт відправляє серверу
    :param start_response: функція, яку сервер викликає для відповіді клієнту
    :return: список байтів закодованої html-сторінки відповіді
    """
    # Якщо шлях URL-запиту є пустим
    if environ.get("PATH_INFO", "").lstrip("/") == "":
        # Створюємо контейнер і передаємо йому дані з форми
        form = cgi.FieldStorage(fp=environ["wsgi.input"], environ=environ)
        string = form.getfirst("string", "")
        char = form.getfirst("char", "")
        # Визначаємо результат
        if string == "" or char == "":
            result = ""
        else:
            idx_res, n_res = search_char(string, char)
            result = format_string(string, char, idx_res, n_res)
            result = f"<h1>{result}</h1>"
        # Створюємо успішну відповідь
        start_response("200 OK", [("Content-type", "text/html; charset=utf-8"), ])
        with open("templates/result.html", encoding="utf-8") as f:
            page = Template(f.read()).substitute(result=result)
    else:
        # У випадку помилки, відправляємо відповідь-повідомлення з описом помилки
        start_response("404 NOT FOUND", [("Content-type", "text/html; charset=utf-8"), ])
        with open("templates/error_404.html", encoding="utf-8") as f:
            page = f.read()

    return [bytes(page, encoding="utf-8")]


HOST = ""
PORT = 8000

if __name__ == '__main__':
    # Створюємо та запускаємо веб-сервер
    from wsgiref.simple_server import make_server
    print(" === Local webserver === ")
    make_server(HOST, PORT, application).serve_forever()