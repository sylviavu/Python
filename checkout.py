import item
from copy import copy, deepcopy

class Checkout:

    receipt_index = 3

    def __init__(self):
        self.receipt = ["'''",
                        "Item                          Price",    # width = 35
                        "----                          -----",
                        ]
        self.basket = []      # holds Item objects
        self.receipt_index = 3
        self.discounted_items = []
        self.all_items = []
        self.quantities = dict()      
        self.checkout_done = False
        

    # retrieve available items
    def getAvailableItems(self, inventory):
        available = "Available items are: "
        for i, item in enumerate(inventory):
            inventory_len = len(inventory)
            if i == inventory_len-1:
                available += (inventory.get(item)[0] + "(%s)" % item)
            else:
                available += (inventory.get(item)[0] + " (%s), " % item)
        return available


    def ScanItems(self, inventory, curr_item):

        if curr_item in "REGISTER":     # show current receipt
            self.PrintReceipt(inventory)
        
        elif curr_item in "DONE":       # determine total price and print entire receipt
            self.FinishCheckout(inventory)

        else:
            while curr_item not in inventory.keys():          # if input is invalid, re-prompt user
                print()
                print("****** Sorry, the item/input entered is invalid. Please try again! ******")  
                print()    
                self.PromptUser(inventory)
            
            temp_item = item.Item(curr_item, inventory.get(curr_item)[1], False, self.receipt_index, self.receipt_index)      # price will be retail price of that item
            self.all_items.append(temp_item)
            self.basket.append(temp_item)
            self.UpdateReceipt(temp_item, self.receipt_index, inventory, False, "")
            self.CheckForDiscounts(temp_item, inventory)
            self.PromptUser(inventory)
            
            
    def CheckForDiscounts(self, item, inventory):
        count = 0
        temp_list = []
        og_item = None

        # buy one CF1 get one free
        if item.code == "CF1":
            for temp in self.basket:
                if temp.code == "CF1":
                    count += 1
                    temp_list.append(temp)      # will add coffee from first scanned to last scanned
            
            while not count % 2 and count > 0:                # for every pair of coffee
                for i in range(2):
                    temp_item = temp_list.pop(0)
                    copy_item = temp_item
                    #temp_item.discount = True
                    if i == 1:
                        temp_item.price = 0.00
                        self.UpdateReceipt(temp_item, copy_item.index, inventory, True, "BOGO")          
                    self.discounted_items.append(temp_item)     # item to new list
                    self.basket.remove(copy_item)               # remove item from original list
                                                                # after exiting the while loop, should be 0 or 1 CH1 in the basket
                    count -= 1                                  # decrement count
        
        # if you buy 3 or more apples, each apple costs $4.50 (prev $6.00)
        # if you buy a bag of oatmeal you get 50% off a bag of apples
        elif item.code == "AP1":
            ap_count = 0
            apom_ap = 0
            apom_om = 0
            apom_valid = True

            # if apples are scanned and there is already oatmeal in the cart, make the apples 50% off
            # LIMIT 1
            for i, this in enumerate(self.basket):
                if this.code == "OM1":
                    for a in self.discounted_items:
                        if a.code in "OM1":
                            apom_om += 1
                        if a.code in "AP1":
                            apom_ap += 1
                        if apom_om >= 1 and apom_ap >= 1:
                            apom_valid = False
                                
                    if apom_valid:        
                        temp_oatmeal = self.basket.pop(i)
                        self.all_items[self.all_items.index(item)].price = inventory.get(item.code)[1] / 2  # apples 1/2 off
                        temp_apples = self.basket.pop(self.basket.index(item))
                        temp_apples.price = inventory.get(item.code)[1] / 2
                        self.discounted_items.append(temp_oatmeal)
                        self.discounted_items.append(temp_apples)
                        self.UpdateReceipt(temp_apples, temp_apples.index, inventory, True, "APOM")
                        return

            # check if 3 or more apples have already been scanned
            # make sure that APOM discount is not part of this apple count
            # if applicable, only one OM1 should be in discounted_items
            for check_item in self.discounted_items:      
                if check_item.code in "AP1":
                    ap_count += 1
                if check_item.code in "OM1":
                    ap_count -= 1
                
            
            if ap_count >= 3:
                temp_item = self.basket.pop(self.basket.index(item))          # apple item
                self.all_items[self.all_items.index(temp_item)].price = 4.50    # change apple price
                temp = self.all_items[self.all_items.index(temp_item)]
                self.discounted_items.append(temp)
                self.UpdateReceipt(temp, temp.index, inventory, True, "APPL")
                return

            # if 3 or more apples have not already been scanned, check how many apples are in the basket
            ap_count = 0
            for i, this in enumerate(self.basket):
                if this.code == "AP1":
                    ap_count += 1

            if ap_count >= 3:
                j = 0
                while ap_count > 0 and j < len(self.basket):
                    if self.basket[j].code in "AP1":    
                        temp_item = self.basket.pop(j)      # remove the item from the basket
                        self.all_items[self.all_items.index(temp_item)].price = 4.50
                        tmp = self.all_items[self.all_items.index(temp_item)]                  # change the item's price in all_items
                        self.discounted_items.append(tmp)  
                        self.UpdateReceipt(tmp, tmp.index, inventory, True, "APPL")
                    else:
                        j += 1
                        

                        
        # purchase a box of chai and get milk free    
        # LIMIT 1
        elif item.code == "MK1" or item.code == "CH1":
            milk_count = 0
            chai_count = 0
            for i in self.discounted_items:     # check if a CHMK discount has already been accounted for
                if i.code in "CH1":
                    chai_count += 1
                elif i.code in "MK1":
                    milk_count += 1
                if chai_count >= 1 and milk_count >= 1:
                    return
            
            # if milk was just scanned, check if there is chai already in the basket
            if item.code == "MK1":
                for i in self.basket:
                    if i.code == "CH1":
                        self.all_items[self.all_items.index(item)].price = 0.00     # make milk free
                        update_item = self.all_items[self.all_items.index(item)]
                        temp_chai = self.basket.pop(self.basket.index(i))
                        temp_milk = self.basket.pop(self.basket.index(item))
                        temp_milk.price = 0.00
                        self.discounted_items.append(temp_chai)
                        self.discounted_items.append(temp_milk)
                        self.UpdateReceipt(update_item, update_item.index, inventory, True, "CHMK")     # update receipt with milk item 
                        return  

            # if chai was just scanned, check if there is milk already in the basket
            # if so, make the milk free
            elif item.code == "CH1":
                for i in self.basket:
                    if i.code == "MK1":
                        self.all_items[self.all_items.index(i)].price = 0.00
                        update_item = self.all_items[self.all_items.index(i)]
                        temp_milk = self.basket.pop(self.basket.index(i))
                        temp_chai = self.basket.pop(self.basket.index(item))
                        self.discounted_items.append(temp_chai)
                        self.discounted_items.append(temp_milk)
                        self.UpdateReceipt(update_item, update_item.index, inventory, True, "CHMK")   
                        return
        
        # purchase a bag of oatmeal and get 50% off a bag of apples
        # if there are no more apples in the basket, apply 50% off to the last bag of apples in discounted_items
        elif item.code == "OM1":
            apom_ap = 0
            apom_om = 0
            apom_valid = True

            for i, this in enumerate(self.basket):
                if this.code == "OM1":
                    for a in self.discounted_items:
                        if a.code in "OM1":
                            apom_om += 1
                        if a.code in "AP1":
                            apom_ap += 1
                        if apom_om >= 1 and apom_ap >= 1:
                            apom_valid = False

            if apom_valid:
                for i in self.basket:
                    if i.code == "AP1":
                        self.all_items[self.all_items.index(i)].price = inventory.get(i.code)[1] / 2       # price of apples 1/2 off
                        temp_oatmeal = self.basket.pop(self.basket.index(item))
                        temp_apples = self.basket.pop(self.basket.index(i))
                        temp_apples.price = inventory.get(i.code)[1] / 2
                        self.discounted_items.append(temp_oatmeal)
                        self.discounted_items.append(temp_apples)
                        self.UpdateReceipt(temp_apples, temp_apples.index, inventory, True, "APOM") 
                        return      
        
        return


    def PrintReceipt(self, inventory):
        print()
        total = 0.00
        for line in self.receipt:
            print(str(line))
        print("-----------------------------------")
        
        self.discounted_items.extend(self.basket)

        for i in range(len(self.discounted_items)):
            total += self.discounted_items[i].price
        
        price_length = len(str(total))
        print(" "*(35-price_length) + "{:0.2f}".format(total))
        print("\'\'\'")

        self.PromptUser(inventory)


    def UpdateReceipt(self, item, index, inventory, is_discounted, discount_code):
        if is_discounted:
            og_price = inventory.get(item.code)[1]      # get original price of item
            discounted_price = og_price - item.price
            price_length = len(str(discounted_price))
            if str(discounted_price)[len(str(discounted_price))-1] in "0":
                price_length += 1
            spacing = 35 - 12 - 4 - price_length - 1
            item.discount = "{space:12}{discount}".format(
                space = " ", 
                discount = discount_code) + " "*spacing + "{minus}{price:.2f}".format(
                minus = "-",
                price = discounted_price)   # format discount string
            self.receipt.insert(item.discount_index, item.discount)         # insert discount string after original item string

            #if self.all_items.index(item) != len(self.all_items)-1:
            temp_index = item.discount_index + 1
            for i in range(len(self.all_items)):
                if i > self.all_items.index(item):
                    self.all_items[i].index = temp_index
                    self.all_items[i].discount_index = temp_index + 1
                    temp_index += 1

            self.receipt_index += 1            
     
        else:
            price_length = len(str(item.price))
            if price_length == 3 or str(item.price)[len(str(item.price))-1] in "0":
                price_length += 1
            spacing = 35 - 3 - price_length 
            new_line = "{code:<3}".format(code = item.code) + " "*spacing + "{price:.2f}".format(
                price = item.price)
            self.receipt.append(new_line)    # add item to receipt
            self.receipt_index += 1

    def FinishCheckout(self, inventory):
        print()
        total = 0.00
        for line in self.receipt:
            print(str(line))
        print("-----------------------------------")
        
        self.discounted_items.extend(self.basket)

        for i in range(len(self.discounted_items)):
            total += self.discounted_items[i].price
        
        total = round(total, 2)
        price_length = len(str(total))
        if price_length == 3 or str(total)[len(str(total))-1] in "0":
            price_length += 1
        space_length = 35 - price_length
        print(" "*space_length + "{total:>.2f}".format(total = total))
        print("\'\'\'")
        print("Thank you for shopping with us! We hope to see you again!")
        print("""
        
        """)


    def PromptUser(self, inventory):
        print()
        print(self.getAvailableItems(inventory))
        curr_item = str(input("""
        Options:
        a.) Enter an item's product code 
        b.) Type \"register\" to view the state of your basket 
        c.) Type \"done\" to finish checking out
        Enter input here: """))    
        curr_item = curr_item.upper()       # change input to uppercase
        self.ScanItems(inventory, curr_item)
