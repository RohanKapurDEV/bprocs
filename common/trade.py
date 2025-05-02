class Trade:
    def __init__(self, price, quantity, timestamp):
        self.price = float(price)
        self.quantity = float(quantity)
        self.timestamp = int(timestamp)

    def to_dict(self):
        return {
            "price": self.price,
            "quantity": self.quantity,
            "timestamp": self.timestamp,
        }

    def __repr__(self):
        return f"Trade(price={self.price}, quantity={self.quantity}, timestamp={self.timestamp})"
