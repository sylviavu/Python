import checkout

class Main:

    inventory_dict = dict()     # key: product code     value: [name, price]
    
    def __init__(self):
        pass
    
    def run_main(self):
        self.readFile()
    
    def readFile(self):
        line = ""
        price = 0.00
        with open("inventory.txt", "r") as reader:
                line = reader.readline()
                while line != '':
                    code, name, price = line.split()
                    price = float(price)
                    self.inventory_dict[code] = [name, price]      # account for product code/price
                    line = reader.readline()        # advance to next line
        reader.close()

new_main = Main()
new_checkout = checkout.Checkout()
new_main.readFile()

new_checkout.PromptUser(new_main.inventory_dict)
