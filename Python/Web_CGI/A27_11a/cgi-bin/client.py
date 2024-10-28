""" [B]27.11.
Скласти програму, яка працює в оточенні веб-сервера, для розв’язання задачі.
Знайти у даному рядку символ та довжину найдовшої послідовності однакових
символів, що йдуть підряд.
Для введення рядка використати одне поле введення на сторінці.
Показати рядок на окремій сторінці, виділивши знайдену найдовшу послідовність
іншим кольором.
a) використати CGI
"""
# Цей файл знаходиться у директорії /cgi-bin/

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

if __name__ == '__main__':
    form = cgi.FieldStorage()  # Створюємо контейнер і отримуємо дані з форми
    # Беремо перше значення (атрибут value) з ім'ям (атрибут name) "string"
    # якщо такого поля в формі немає, то беремо пустий рядок
    string = form.getfirst("string", "")
    char = form.getfirst("char", "")
    idx_res, n_res = search_char(string, char)
    result = format_string(string, char, idx_res, n_res)

    # Відкриваємо шаблон
    with open("result.html", encoding="utf-8") as f:
        # Зчитуємо дані і підставляємо результат
        page = Template(f.read()).substitute(result=result)

    import os  # Якщо у нас операційна система Windows, то змінюємо кодування
    if os.name == "nt":
        import sys, codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer)

    # додаємо заголовок та друкуємо сторінку в веб-браузер
    print("Content-type: text/html charset=utf-8\n")
    print(page)