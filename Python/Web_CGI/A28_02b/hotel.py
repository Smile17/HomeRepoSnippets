class HotelNumber:
    def __init__(self, number, hotel_type, price_per_night):
        self.number = number
        self.hotel_type = hotel_type
        self.price_per_night = price_per_night


class Guest:
    def __init__(self, full_name, hotel_number, num_of_days):
        self.full_name = full_name
        self.hotel_number = hotel_number
        self.num_of_days = num_of_days

    def total_price(self):
        return self.num_of_days * self.hotel_number.price_per_night

