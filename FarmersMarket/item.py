#import Main
#import Checkout
#from Main import main

class Item:

    def __init__(self, product_code, price, discount, index, discount_index):
        self.code = product_code
        self.price = price
        self.discount = ""
        self.index = index
        self.discount_index = index + 1