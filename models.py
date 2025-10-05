class Product:
    def __init__(self, product_id, product_name):
        self.product_id = product_id
        self.product_name = product_name

class Location:
    def __init__(self, location_id, location_name):
        self.location_id = location_id
        self.location_name = location_name

class ProductMovement:
    def __init__(self, movement_id, timestamp, from_location, to_location, product_id, qty):
        self.movement_id = movement_id
        self.timestamp = timestamp
        self.from_location = from_location
        self.to_location = to_location
        self.product_id = product_id
        self.qty = qty