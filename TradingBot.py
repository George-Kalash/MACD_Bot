



class TradingBot:
    def __init__(self, name, initial_balance):
        self.name = name
        self.balance = initial_balance
        self.portfolio = {}

    def buy(self, asset, quantity, price):
        total_cost = quantity * price
        if total_cost > self.balance:
            raise ValueError("Insufficient balance to complete the purchase.")
        self.balance -= total_cost
        if asset in self.portfolio:
            self.portfolio[asset] += quantity
        else:
            self.portfolio[asset] = quantity

    def sell(self, asset, quantity, price):
        if asset not in self.portfolio or self.portfolio[asset] < quantity:
            raise ValueError("Insufficient asset quantity to complete the sale.")
        total_revenue = quantity * price
        self.balance += total_revenue
        self.portfolio[asset] -= quantity
        if self.portfolio[asset] == 0:
            del self.portfolio[asset]

    def get_balance(self):
        return self.balance

    def get_portfolio(self):
        return self.portfolio