import sqlite3

conn = sqlite3.connect('all_transactions.db')

c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS all_transactions
(name text, sp real, date text, pp real)""")


def addData(itemName, salePrice, date, purchasePrice):
    params = (itemName, salePrice, date, purchasePrice)
    c.execute("INSERT INTO all_transactions VALUES (?, ?, ?, ?)", params)
    conn.commit()
    print("Transaction was added!")


def getData():
    c.execute("SELECT * FROM all_transactions")
    rows = c.fetchall()
    # print("NAME/BARCODE/PURCHASE PRICE/SALE PRICE/QUANTITY")

    return list(rows)


def deleteData():
    c.execute("DELETE FROM all_transactions")
    print("Data was deleted!")


conn.commit()
