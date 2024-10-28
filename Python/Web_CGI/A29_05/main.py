"""
[B]29.05. Скласти програму, яка працює в оточенні веб-сервера, для розрахунку плати
за проживання гостя в готелі.
Описати клас Номер з полями «тип», «плата за добу» та клас Гість з полями «ПІБ»,
«номер», «кількість діб проживання».
Використати ці класи для реєстрації гостя у номері та розрахунку плати за
проживання усіх гостей.
Номери та інформація про гостей зберігаються у базі даних у окремих таблицях.
Програма повинна передбачати реєстрацію гостя на окремій сторінці. При реєстрації
вибрати номер зі списку номерів та вказати кількість діб проживання. На іншій
сторінці показувати список гостей та плату за проживання кожного гостя.
Забезпечити можливість редагування інформації про гостя, який проживає в готелі,
та звільнення гостем номеру.
"""

from wsgiref.simple_server import make_server
from string import Template
import cgi
import sqlite3
import os

# шаблон для списку кімнат для випадаючого списку при реєстрації
OPTION_ID = """
      <option value="$reserv">$reserv</option>
"""
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
                <td>$room_avail</td>
            </tr>
"""
# шаблон для резервації для таблиці всіх резервацій
HOTEL_RESERV_ROW = """
            <tr>
                    <td>$full_name</td>
                    <td>$number</td>
                    <td>$num_nights</td>
                    <td>$total_price</td>
                    <td>$is_living</td>
            </tr>
"""


class HotelDB:

    def __init__(self, database):
        self.database = database

    def get_rooms(self):
        """ Повертає список з БД"""
        conn = sqlite3.connect(self.database)
        curs = conn.cursor()
        curs.execute("""SELECT * FROM "hotel_rooms";""")
        rooms = curs.fetchall()
        conn.close()
        return rooms

    def register_guest(self, full_name, number, number_of_night):
        conn = sqlite3.connect(self.database)
        curs = conn.cursor()
        insert_query = """
                    INSERT INTO
                        "guests" ("full_name", "hotel_room_id", "number_of_night")
                    VALUES
                """ + f"""("{full_name}", {number}, "{number_of_night}")"""
        curs.execute(insert_query)
        update_query = f"""UPDATE "hotel_rooms" set "is_available" = false
                        WHERE "id" = {number}
        """
        curs.execute(update_query)
        conn.commit()
        conn.close()

    def get_hotel_reservations(self): # завантажує всі резервації
        """ Повертає список з БД"""
        conn = sqlite3.connect(self.database)
        curs = conn.cursor()
        curs.execute("""SELECT "guests"."id", "full_name", "hotel_room_id", "number_of_night", "number_of_night" * "price", "is_living"
                        FROM "guests"
                        INNER JOIN "hotel_rooms"
                                ON "hotel_rooms"."id" = "guests"."hotel_room_id"
        ;""")
        records = curs.fetchall()
        conn.close()
        return records

    def update_guest(self, guest_id, full_name, number_of_night):
        conn = sqlite3.connect(self.database)
        curs = conn.cursor()

        update_query = f"""
                    UPDATE
                        "guests" set "full_name" = "{full_name}",
                        "number_of_night" = {number_of_night}
                        WHERE "id" = {guest_id}
"""
        curs.execute(update_query)
        conn.commit()
        conn.close()

    def update_guest_room(self, guest_id, old_number, new_number):
        conn = sqlite3.connect(self.database)
        curs = conn.cursor()

        update_query = f"""
                        UPDATE
                        "guests" set "hotel_room_id" = {new_number}
                            WHERE "id" = {guest_id};  
        """
        curs.execute(update_query)
        update_query = f"""
                                
                                UPDATE
                                    "hotel_rooms" set "is_available" = True
                                    WHERE "id" = {old_number};
                                 
                """
        curs.execute(update_query)
        update_query = f"""
                               
                                UPDATE
                                    "hotel_rooms" set "is_available" = False
                                    WHERE "id" = {new_number};    
                """
        curs.execute(update_query)
        conn.commit()
        conn.close()

    def leave_guest_room(self, guest_id, room_id):
        conn = sqlite3.connect(self.database)
        curs = conn.cursor()

        update_query = f"""
                        UPDATE
                        "guests" set "is_living" = False
                            WHERE "id" = {guest_id};  
        """
        curs.execute(update_query)
        update_query = f"""

                                UPDATE
                                    "hotel_rooms" set "is_available" = True
                                    WHERE "id" = {room_id};    
                """
        curs.execute(update_query)
        conn.commit()
        conn.close()

    def get_hotel_reservation(self, guest_id): # завантажує всі резервації
        """ Повертає список з БД"""
        conn = sqlite3.connect(self.database)
        curs = conn.cursor()
        curs.execute(f"""SELECT * FROM "guests"
                        WHERE "id" = {guest_id}
        ;""")
        records = curs.fetchall()
        conn.close()
        return records

    def get_hotel_reservation_active(self):  # завантажує всі резервації
        """ Повертає список з БД"""
        conn = sqlite3.connect(self.database)
        curs = conn.cursor()
        curs.execute("""SELECT "guests"."id", "full_name", "hotel_room_id", "number_of_night", "number_of_night" * "price", "is_living"
                        FROM "guests"
                        
                        INNER JOIN "hotel_rooms"
                                ON "hotel_rooms"."id" = "guests"."hotel_room_id"
                        WHERE "is_living" = 1
        ;""")
        records = curs.fetchall()
        conn.close()
        return records

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "").lstrip("/")
        params = {"hotel_rooms": "", "hotel_numbers": "", "hotel_reservations": "", "result": ""}
        status = "200 OK"
        headers = [("Content-Type", "text/html; charset=utf-8")]
        file = "templates/main.html"
        form = cgi.FieldStorage(fp=environ["wsgi.input"], environ=environ)

        # http://localhost:8000/
        if path == "":
            # Реєструємо нового гостя, якщо дані введені
            full_name = form.getfirst("full_name", "")
            hotel_num = form.getfirst("hotel", "")
            num_of_days = form.getfirst("num_of_days", "")
            if full_name != "" and hotel_num != "" and num_of_days != "":
                self.register_guest(full_name, hotel_num, num_of_days)
            # End registration

            # Підтягуємо всі кімнати
            hotel_rooms = ""
            hotel_numbers = ""
            rooms = self.get_rooms()
            for room in rooms:
                hotel_rooms += Template(HOTEL_ROOMS_ROW).substitute(room_num=room[0],
                                                                    room_type=room[1],
                                                                    room_price=room[2],
                                                                    room_avail="Доступна" if room[3] == 1 else "Не доступна")
                if room[3] == 1:
                    hotel_numbers += Template(OPTION).substitute(room=room[0])

            params["hotel_rooms"] = hotel_rooms
            params["hotel_numbers"] = hotel_numbers

            # Підтягуємо всі резервації
            hotel_reservations = ""
            guests = self.get_hotel_reservations()
            for reser in guests:
                hotel_reservations += Template(HOTEL_RESERV_ROW).substitute(full_name=reser[1],
                                                                            number=reser[2],
                                                                            num_nights=reser[3],
                                                                            total_price=reser[4],
                                                                            is_living="Мешкає" if reser[5] == 1 else "Не мешкає"
                                                                            )
            params["hotel_reservations"] = hotel_reservations

        elif path == "all_reservations":
            file = "templates/all_reservations.html"
            # Підтягуємо всі резервації
            hotel_reservations = ""
            guests = self.get_hotel_reservations()
            for reser in guests:
                hotel_reservations += Template(HOTEL_RESERV_ROW).substitute(full_name=reser[1],
                                                                            number=reser[2],
                                                                            num_nights=reser[3],
                                                                            total_price=reser[4],
                                                                            is_living="Мешкає" if reser[
                                                                                                      5] == 1 else "Не мешкає"
                                                                            )
            params["hotel_reservations"] = hotel_reservations
        elif path == "edit_reservation":
            file = "templates/edit_reservation.html"
            id = form.getfirst("reser_id", "")
            full_name = form.getfirst("full_name", "")
            number_of_nights = form.getfirst("number_of_nights", "")

            # Підтягуємо всі резервації
            hotel_reservations = ""
            guests = self.get_hotel_reservation_active()
            for reser in guests:
                hotel_reservations += Template(OPTION_ID).substitute(reserv=reser[0])
            params["reservations"] = hotel_reservations

            # Якщо запит до стрінки надійшов з форми для зміни
            if id:
                self.update_guest(id, full_name, number_of_nights)
                params["result"] += (
                    f"Дані резервації \"{id}\" успішно змінено на ПІБ: \"{full_name}\", Кількість діб: \"{number_of_nights}\"! "
                )

        elif path == "change_room":
            file = "templates/change_room.html"
            id = form.getfirst("reser_id", "")
            hotel_number = form.getfirst("hotel", "")

            # Підтягуємо всі кімнати
            hotel_rooms = ""
            hotel_numbers = ""
            rooms = self.get_rooms()
            for room in rooms:
                hotel_rooms += Template(HOTEL_ROOMS_ROW).substitute(room_num=room[0],
                                                                    room_type=room[1],
                                                                    room_price=room[2],
                                                                    room_avail="Доступна" if room[
                                                                                                 3] == 1 else "Не доступна")
                if room[3] == 1:
                    hotel_numbers += Template(OPTION).substitute(room=room[0])

            params["hotel_rooms"] = hotel_rooms
            params["hotel_numbers"] = hotel_numbers

            # Підтягуємо всі резервації
            hotel_reservations = ""
            guests = self.get_hotel_reservation_active()
            for reser in guests:
                hotel_reservations += Template(OPTION_ID).substitute(reserv=reser[0])
            params["reservations"] = hotel_reservations

            # Якщо запит до стрінки надійшов з форми для зміни
            if id:
                reservation = self.get_hotel_reservation(id)[0]
                self.update_guest_room(id, reservation[2], hotel_number)
                params["result"] += (
                    f"Дані резервації \"{id}\" успішно змінено на кімнату: \"{hotel_number}\"! "
                )

        elif path == "leave_room":
            file = "templates/leave_room.html"
            id = form.getfirst("reser_id", "")

            # Підтягуємо всі резервації
            hotel_reservations = ""
            guests = self.get_hotel_reservation_active()
            for reser in guests:
                hotel_reservations += Template(OPTION_ID).substitute(reserv=reser[0])
            params["reservations"] = hotel_reservations

            # Якщо запит до стрінки надійшов з форми для зміни
            if id:
                reservation = self.get_hotel_reservation(id)[0]
                params["hotel_numbers"] = reservation[2]
                self.leave_guest_room(id, reservation[2])
                params["result"] += (
                    f"Дані резервації \"{id}\" успішно змінено, кімнату звільнено! "
                )

        # http://localhost:8000/<будь-який інший запит>
        else:
            status = "404 NOT FOUND"
            file = "templates/error_404.html"

        start_response(status, headers)
        with open(file, encoding="utf-8") as f:
            page = Template(f.read()).substitute(params)
        return [bytes(page, encoding="utf-8")]

import json
def get_hotel_rooms(json_filename): # завантажує всі кімнати
    with open(json_filename) as f:
        lst = json.load(f)
    return [(dct["number"], dct["type"], dct["price_per_night"]) for dct in lst]

def restore_db(json_filename, db_filename):
    """ Створює або оновлює БД з заданого JSON-файлу.

    :param json_filename: назва json-файлу
    :param db_filename: назва БД
    :return:
    """
    if os.path.exists(db_filename):
        os.remove(db_filename)

    conn = sqlite3.connect(db_filename)
    curs = conn.cursor()
    # Створюємо таблиці
    curs.executescript(
        """
        CREATE TABLE "hotel_rooms" (
            "id" TEXT UNIQUE NOT NULL,
            "type" TEXT NOT NULL,
            "price" REAL NOT NULL,
            "is_available" BOOLEAN DEFAULT TRUE,
            PRIMARY KEY ("id")
        );
        CREATE TABLE "guests" (
            "id" INTEGER PRIMARY KEY AUTOINCREMENT,
            "full_name" TEXT NOT NULL,
            "hotel_room_id" TEXT NOT NULL,
            "number_of_night" INT NOT NULL,
            "is_living" BOOLEAN DEFAULT TRUE,
            CHECK ("number_of_night">0),
            FOREIGN KEY ("hotel_room_id") REFERENCES "hotel_rooms" ("id")
        );
        """
    )
    # Записуємо дані з робочої книги Excel до БД
    rooms  = get_hotel_rooms(json_filename)
    records = [f"""('{room[0]}', '{room[1]}', '{room[2]}')""" for room in rooms]
    insert_query = """
        INSERT INTO
            "hotel_rooms" ("id", "type", "price")
        VALUES
    """ + ",\n".join(list(records)) + ";"
    print(insert_query)
    curs.execute(insert_query)
    conn.commit()
    conn.close()


HOST = ""
PORT = 8000

if __name__ == "__main__":
    hotel_path = "data/hotel.json"
    db = "data/hotel.db"
    restore_db(hotel_path, db)
    app = HotelDB(db)
    print(f"Локальний сервер запущено на http://localhost:{PORT}")
    make_server(HOST, PORT, app).serve_forever()
