import sqlite3

conn = sqlite3.connect('transactions.db')

c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS transactions
(name text, sp real, date text)""")


def addData(itemName, salePrice, date):
    params = (itemName, salePrice, date)
    c.execute("INSERT INTO transactions VALUES (?, ?, ?)", params)
    conn.commit()
    print("Transaction was added!")


def getData():
    c.execute("SELECT * FROM transactions")
    rows = c.fetchall()
    # print("NAME/BARCODE/PURCHASE PRICE/SALE PRICE/QUANTITY")

    return list(rows)


def deleteData():
    c.execute("DELETE FROM transactions")
    print("Data was deleted!")


conn.commit()
