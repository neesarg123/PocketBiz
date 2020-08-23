import sqlite3

conn = sqlite3.connect('items.db')

c = conn.cursor()

# creating a database at the first run
c.execute("""CREATE TABLE IF NOT EXISTS items
(name text, barcode integer, pp real, sp real, qtn integer, op real, tax text)""")


# adding items into the database
def addData(item_name, barcode_number, purchase_price, sale_price, quantity, online_price, tax):
    params = (item_name, barcode_number, purchase_price, sale_price, quantity, online_price, tax)
    c.execute("INSERT INTO items VALUES (?, ?, ?, ?, ?, ?, ?)", params)
    conn.commit()


# fetching the items in the database
def getData():
    c.execute("SELECT * FROM items")
    rows = c.fetchall()
    return list(rows)


# fetching only names from database
def getNames():
    c.execute("SELECT name FROM items")
    rows = c.fetchall()
    return list(rows)


# fetching only barcodes from database
def getBarcodes():
    c.execute("SELECT barcode FROM items")
    rows = c.fetchall()
    return list(rows)


# fetching barcodes from name and sp
def getBarcodeFromNameSP(name, sp):
    params = (name, sp)
    try:
        b = c.execute("SELECT barcode FROM items WHERE name = (?) AND sp = (?)", params)
        final_b = b.fetchone()
        return str(final_b[0])
    except Exception:
        pass


# fetching only purchase prices from database
def getPPrices():
    c.execute("SELECT pp FROM items")
    rows = c.fetchall()
    return list(rows)


# fetching only sale prices from database
def getSPrices():
    c.execute("SELECT sp FROM items")
    rows = c.fetchall()
    return list(rows)


# fetching only quantities from database
def getQtns():
    c.execute("SELECT qtn FROM items")
    rows = c.fetchall()
    return list(rows)


# fetching only online prices from database
def getOPs():
    c.execute("SELECT op FROM items")
    rows = c.fetchall()
    return list(rows)


# fetching only tax prices from database
def getTaxes():
    c.execute("SELECT tax FROM items")
    rows = c.fetchall()
    return list(rows)


# adding a functions which will allow the name, p.price, s.price, and quantity to be changed
def updateName(new_name, barcode_number):
    params = (new_name, barcode_number)
    try:
        c.execute("UPDATE items SET name = (?) WHERE barcode = (?)", params)
        conn.commit()
    except Exception:
        pass


def updatePurchasePrice(new_pp, barcode_number):
    params = (new_pp, barcode_number)
    try:
        c.execute("UPDATE items SET pp = (?) WHERE barcode = (?)", params)
        conn.commit()
    except Exception:
        pass


def updateSalePrice(new_sp, barcode_number):
    params = (new_sp, barcode_number)
    try:
        c.execute("UPDATE items SET sp = (?) WHERE barcode = (?)", params)
        conn.commit()
    except Exception:
        pass


def updateQuantity(new_qtn, barcode_number):
    params = (new_qtn, barcode_number)
    try:
        c.execute("UPDATE items SET qtn = (?) WHERE barcode = (?)", params)
        conn.commit()
    except Exception:
        pass


def updateOP(new_op, barcode_number):
    params = (new_op, barcode_number)
    try:
        c.execute("UPDATE items SET op = (?) WHERE barcode = (?)", params)
        conn.commit()
    except Exception:
        pass


# adding functions that will allow name, s.price, p.price, and quantity to be returned given barcode
def getSalePriceFromBarcode(barcode_number):
    param = (barcode_number,)
    try:
        sale_price = c.execute("SELECT sp FROM items WHERE  barcode = (?)", param)
        final_sale_price = sale_price.fetchone()
        return final_sale_price[0]
    except Exception:
        pass


def getNameFromBarcode(barcode_number):
    param = (barcode_number,)
    try:
        name = c.execute("SELECT name FROM items WHERE barcode = (?)", param)
        final_name = name.fetchone()
        return str(final_name[0])
    except Exception:
        pass


def getPPFromBarcode(barcode_number):
    param = (barcode_number,)
    try:
        pp = c.execute("SELECT pp FROM items WHERE barcode = (?)", param)
        final_pp = pp.fetchone()
        return str(final_pp[0])
    except Exception:
        pass


def getQtnFromBarcode(barcode_number):
    param = (barcode_number,)
    try:
        pp = c.execute("SELECT qtn FROM items WHERE barcode = (?)", param)
        final_qtn = pp.fetchone()
        return str(final_qtn[0])
    except Exception:
        pass


def getOPFromBarcode(barcode_number):
    param = (barcode_number,)
    try:
        pp = c.execute("SELECT op FROM items WHERE barcode = (?)", param)
        final_op = pp.fetchone()
        return str(final_op[0])
    except Exception:
        pass


def getTaxableFromNameAndSP(name, sp):
    params = (name, sp)
    try:
        t = c.execute("SELECT tax FROM items WHERE name = (?) AND sp = (?)", params)
        final_t = t.fetchone()
        return str(final_t[0])
    except Exception:
        pass


def getTaxableFromNameAndOP(name, op):
    params = (name, op)
    try:
        t = c.execute("SELECT tax FROM items WHERE name = (?) AND op = (?)", params)
        final_t = t.fetchone()
        return str(final_t[0])
    except Exception:
        pass


# adding a function that will decrement quantity of an item as it is transacted
def decreaseQuantityByOne(barcode_number):
    try:
        originalQtn = getQtnFromBarcode(barcode_number)
        newQtn = int(originalQtn) - 1
        params = (newQtn, barcode_number)

        try:
            c.execute("UPDATE items SET qtn = (?) WHERE barcode = (?)", params)
            conn.commit()
        except Exception:
            pass
    except TypeError:
        pass


def deleteData():
    c.execute("DELETE FROM items")


conn.commit()
