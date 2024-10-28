"""
[B]28.05. Скласти програму, яка працює в оточенні веб-сервера, для розрахунку плати
за проживання гостя в готелі.
Описати клас Номер з полями «тип», «плата за добу» та клас Гість з полями «ПІБ»,
«номер», «кількість діб проживання».
Використати ці класи для реєстрації гостя у номері та розрахунку плати за
проживання усіх гостей.
Номери та інформацію про гостей зберігати у файлах на сервері.
Програма повинна передбачати реєстрацію гостя на окремій сторінці. При реєстрації
вибрати номер зі списку номерів та вказати кількість діб проживання. Показувати
список гостей та плату за проживання кожного гостя у форматі
Файл номерів, файл гостей та результуючий список гостей мають бути у форматі
a) JSON
Структуру даних JSON/XML визначити самостійно
"""

import json
import cgi
from string import Template
from wsgiref.simple_server import make_server
from hotel import HotelNumber, Guest

# шаблон для списку кімнат для випадаючого списку при реєстрації
OPTION = """
      <option value="$room">$room</option>
"""
# шаблон для кімнати для таблиці всіх кімнат
HOTEL_ROOMS_ROW = """
            <tr>
                <td>$room_num</td>
                <td>$room_type</td>
                <td>$room_price</td>
            </tr>
"""
# шаблон для резервації для таблиці всіх резервацій
HOTEL_RESERV_ROW = """
            <tr>
                    <td>$full_name</td>
                    <td>$number</td>
                    <td>$num_nights</td>
                    <td>$total_price</td>
            </tr>
"""

class HotelJSON:

    def __init__(self, hotel_rooms_path, guests_path):
        self.hotel_rooms_path = hotel_rooms_path # зберігає шлях до всіх кімнат
        self.hotel_rooms = {} # зберігає словник всіх кімнат, ключем є номер кімнати, значенням - обєкт класу HotelNumber
        self.guests_path = guests_path # зберігає шлях до всіх резервацій
        self.guests = []

    def get_hotel_rooms(self): # завантажує всі кімнати
        with open(self.hotel_rooms_path) as f:
            lst = json.load(f)
        return [HotelNumber(dct["number"], dct["type"], dct["price_per_night"]) for dct in lst]

    def get_hotel_reservations(self): # завантажує всі резервації
        with open(self.guests_path) as f:
            lst = json.load(f)
        return [Guest(dct["full_name"], self.hotel_rooms[dct["number"]], dct["num_of_days"]) for dct in lst]


    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "").lstrip("/")
        form = cgi.FieldStorage(fp=environ["wsgi.input"], environ=environ)
        params = {"hotel_rooms": "", "hotel_numbers": "", "hotel_reservations": ""}
        status = "200 OK"
        headers = [("Content-Type", "text/html; charset=utf-8")]
        file = "templates/main.html"

        # http://localhost:8000/
        if path == "":
            # Реєструємо нового гостя, якщо дані введені
            full_name = form.getfirst("full_name", "")
            hotel_num = form.getfirst("hotel", "")
            num_of_days = form.getfirst("num_of_days", "")
            if full_name != "" and hotel_num != "" and num_of_days != "":
                guest = {
                        "full_name": full_name,
                        "number": hotel_num,
                        "num_of_days": int(num_of_days)
                      }
                # Записуємо результат у файл, додаючи його до попередніх замовлень
                with open(self.guests_path, "r+") as f:
                    lst = json.load(f)
                    lst.append(guest)
                    f.seek(0)
                    json.dump(lst, f, indent=4)
            # End registration

            # Підтягуємо всі кімнати
            hotel_rooms = ""
            hotel_numbers = ""
            rooms = self.get_hotel_rooms()
            self.hotel_rooms = {value.number: value for value in rooms}
            for room in rooms:
                hotel_rooms += Template(HOTEL_ROOMS_ROW).substitute(room_num=room.number,
                                                           room_type=room.hotel_type, room_price=room.price_per_night)
                hotel_numbers += Template(OPTION).substitute(room=room.number)

            params["hotel_rooms"] = hotel_rooms
            params["hotel_numbers"] = hotel_numbers

            # Підтягуємо всі резервації
            hotel_reservations = ""
            self.guests = self.get_hotel_reservations()
            for reser in self.guests:
                hotel_reservations += Template(HOTEL_RESERV_ROW ).substitute(full_name=reser.full_name,
                                                                            number=reser.hotel_number.number,
                                                                            num_nights=reser.num_of_days,
                                                                            total_price = reser.total_price())
            params["hotel_reservations"] = hotel_reservations


        # http://localhost:8000/<будь-який інший запит>
        else:
            status = "404 NOT FOUND"
            file = "templates/error_404.html"

        start_response(status, headers)
        with open(file, encoding="utf-8") as f:
            page = Template(f.read()).substitute(params)
        return [bytes(page, encoding="utf-8")]

HOST = ""
PORT = 8000

if __name__ == "__main__":
    app = HotelJSON("data/hotel.json", "data/guests.json")
    print(f"Локальний веб-сервер запущено на http://localhost:{PORT}")
    make_server(HOST, PORT, app).serve_forever()
