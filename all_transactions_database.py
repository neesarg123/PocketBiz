import sqlite3

conn = sqlite3.connect('all_transactions.db')

c = conn.cursor()

# creating a database table (at first run of program since there will be no table yet)
c.execute("""CREATE TABLE IF NOT EXISTS all_transactions
(name text, sp real, date text, payment text, total text)""")


# adding data function which will be called from main to add transactions into the database
def addData(item_name, sale_price, date, payment_type, total):
    params = (item_name, sale_price, date, payment_type, total)
    c.execute("INSERT INTO all_transactions VALUES (?, ?, ?, ?, ?)", params)
    conn.commit()


# obtaining a list of transactions present in the database
def getData():
    c.execute("SELECT * FROM all_transactions")
    rows = c.fetchall()
    return list(rows)


# fetching only names from database
def getNames():
    c.execute("SELECT name FROM all_transactions")
    rows = c.fetchall()
    return list(rows)


# fetching only sale prices from database
def getSPrices():
    c.execute("SELECT sp FROM all_transactions")
    rows = c.fetchall()
    return list(rows)


# fetching only dates from database
def getDates():
    c.execute("SELECT date FROM all_transactions")
    rows = c.fetchall()
    return list(rows)


# fetching only payment types from database
def getPTypes():
    c.execute("SELECT payment FROM all_transactions")
    rows = c.fetchall()
    return list(rows)


# fetching only payment types from database
def getPaymentTypes():
    c.execute("SELECT payment FROM all_transactions")
    rows = c.fetchall()
    return list(rows)


# fetching only payment types from database
def getTotals():
    c.execute("SELECT total FROM all_transactions")
    rows = c.fetchall()
    return list(rows)


# deleting the whole database (just in case function)
def deleteData():
    c.execute("DELETE FROM all_transactions")


conn.commit()
