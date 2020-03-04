import sqlite3

conn = sqlite3.connect('items.db')

c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS items
(name text, barcode integer, pp real, sp real, qtn integer)""")


def addData(itemName, barcodeNumber, purchasePrice, salePrice, quantity):
    params = (itemName, barcodeNumber, purchasePrice, salePrice, quantity)
    c.execute("INSERT INTO items VALUES (?, ?, ?, ?, ?)", params)
    conn.commit()
    print("Item was added!")


def getData():
    c.execute("SELECT * FROM items")
    rows = c.fetchall()
    # print("NAME/BARCODE/PURCHASE PRICE/SALE PRICE/QUANTITY")

    return list(rows)

    quantity_tot = 0

    c.execute("SELECT qtn FROM items")


def updateName(new_name, barcode_number):
    params = (new_name, barcode_number)
    try:
        c.execute("UPDATE items SET name = (?) WHERE barcode = (?)", params)
        conn.commit()
        print("Item name was updated!")
    except:
        print("Sorry, did not find the item!")


def updatePurchasePrice(new_pp, barcode_number):
    params = (new_pp, barcode_number)
    try:
        c.execute("UPDATE items SET pp = (?) WHERE barcode = (?)", params)
        conn.commit()
        print("Item purchase price was updated!")
    except:
        print("Sorry, did not find the item!")


def updateSalePrice(new_sp, barcode_number):
    params = (new_sp, barcode_number)
    try:
        c.execute("UPDATE items SET sp = (?) WHERE barcode = (?)", params)
        conn.commit()
        print("Item sale price was updated!")
    except:
        print("Sorry, did not find the item!")


def updateQuantity(new_qtn, barcode_number):
    params = (new_qtn, barcode_number)
    try:
        c.execute("UPDATE items SET qtn = (?) WHERE barcode = (?)", params)
        conn.commit()
        print("Item quantity was updated!")
    except:
        print("Sorry, did not find the item!")


def getSalePriceFromBarcode(barcode_number):
    param = (barcode_number,)
    try:
        sale_price = c.execute("SELECT sp FROM items WHERE  barcode = (?)", param)
        final_sale_price = sale_price.fetchone()
        return int(final_sale_price[0])
    except:
        print("Sorry, did not find the item!")


def getNameFromBarcode(barcode_number):
    param = (barcode_number,)
    try:
        name = c.execute("SELECT name FROM items WHERE barcode = (?)", param)
        final_name = name.fetchone()
        return str(final_name[0])
    except:
        print("Sorry, did not find the item!")


def getPPFromBarcode(barcode_number):
    param = (barcode_number,)
    try:
        pp = c.execute("SELECT pp FROM items WHERE barcode = (?)", param)
        final_pp = pp.fetchone()
        return str(final_pp[0])
    except:
        print("Sorry, did not find the item!")


def getQtnFromBarcode(barcode_number):
    param = (barcode_number,)
    try:
        pp = c.execute("SELECT qtn FROM items WHERE barcode = (?)", param)
        final_qtn = pp.fetchone()
        return str(final_qtn[0])
    except:
        print("Sorry, did not find the item!")


def decreaseQuantityByOne(barcode_number):
    originalQtn = getQtnFromBarcode(barcode_number)
    newQtn = int(originalQtn) - 1
    params = (newQtn, barcode_number)

    try:
        c.execute("UPDATE items SET qtn = (?) WHERE barcode = (?)", params)
        conn.commit()
        print("Item quantity was updated!")

    except:
        print("Sorry, did not find the item!")


conn.commit()
