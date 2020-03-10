# The point of this file is to store the transactions as they occur in the transaction mode,
# and the whole table will be sent off to all_transactions database to keep track of all transactions.
# Once that occurs, the data in this table will be deleted to be populated once again when a new transaction
# event begins.
import sqlite3

conn = sqlite3.connect('transactions.db')

c = conn.cursor()

# creating a database table at first run
c.execute("""CREATE TABLE IF NOT EXISTS transactions
(name text, sp real, date text)""")


def addData(item_name, sale_price, date):
    params = (item_name, sale_price, date)
    c.execute("INSERT INTO transactions VALUES (?, ?, ?)", params)
    conn.commit()


def getData():
    c.execute("SELECT * FROM transactions")
    rows = c.fetchall()
    return list(rows)


def deleteData():
    c.execute("DELETE FROM transactions")


conn.commit()
