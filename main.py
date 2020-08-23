import tkinter as tk
import item_database
import transactions_database
import all_transactions_database
from tkintertable import TableCanvas, TableModel
import datetime
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from decimal import *
import win32print
import win32api
import win32con
import os.path
import itertools
import pygsheets

# COLORS
BACKGROUND_FRAME_COLOR = '#42423f'
BUTTON_AND_LABEL_COLOR = '#adada6'
BACK_BUTTON_COLOR = '#d93027'
ENTRY_COLOR = '#d9d1d0'

# Return & Discount window
TK_INPUT_WIN_H = 250
TK_INPUT_WIN_W = 250
TK_INPUT_BG = '#575353'
FG_LABELS_COLOR = '#ffffff'
ONLINE_IND_COLOR = '#5dc77a'
OFFLINE_IND_COLOR = '#ed4c40'
YES_BTN = '#82ba6e'
NO_BTN = '#b52438'
# font
FONT = ('Courier', 15, 'bold')

# --------------- PRELIMINARY SETUP --------------- #

# globals
global PRINTER_NAME, G_INV_SH_NAME, G_TRAN_SH_NAME, GC, SH, WKS, SH_T, WKS_T, ALL_TRANSACTIONS, INVENTORY_DF, ON_OFF_CYC

# read inputs text file
input_file = open('inputs.txt', 'r')

for idx, line in enumerate(input_file.readlines()):
    value = line.split("=")[1]
    if idx == 0:
        PRINTER_NAME = value[2:-2]
    elif idx == 1:
        G_INV_SH_NAME = value[2:-2]
    else:
        G_TRAN_SH_NAME = value[2:-1]

# authorize google sheets
if os.path.isfile('creds.json'):
    try:
        GC = pygsheets.authorize(service_file='creds.json')
    except Exception as e:
        print("Something went Wrong while getting authorizing credentials file:", str(e))

    if len(G_INV_SH_NAME) > 0:
        try:
            print("Trying to open the google inventory file...")
            SH = GC.open(G_INV_SH_NAME)
            WKS = SH[0]
            print("Successfully opened the google inventory file!")
        except Exception as e:
            print("Something went wrong while opening the google inventory file:", str(e))

    if len(G_TRAN_SH_NAME) > 0:
        try:
            print("Trying to open the google transactions file...")
            SH_T = GC.open(G_TRAN_SH_NAME)
            WKS_T = SH_T[0]
            print("Successfully opened the google transactions file!")
        except Exception as e:
            print("Something went wrong while opening the google transactions file:", str(e))

else:
    print("You don't yet have a google sheets API set up. Follow this link to set one up:\n"
          "https://developers.google.com/sheets/api/quickstart/python")

""" Checking whether inventory & transactions excel files exist already, 
    if not, then create it. Either way, store the data into data frames. """

if not os.path.isfile('Transactions.xlsx'):
    header_df = pd.DataFrame({'Name': [], 'S.Price': [], 'Date': [], 'P.Type': [],
                              'Total': []})
    header_df.to_excel('Transactions.xlsx', index=False)

ALL_TRANSACTIONS = pd.read_excel('Transactions.xlsx', ignore_index=True)

""" Clean up the database for all transactions, because we want to give priority to changes
    done in the transactions excel file. """

all_transactions_database.deleteData()

# Next, add the data in transactions file into the database
for idx, name in enumerate(list(ALL_TRANSACTIONS['Name'])):
    all_transactions_database.addData(name, str(ALL_TRANSACTIONS['S.Price'][idx]), str(ALL_TRANSACTIONS['Date'][idx]),
                                      str(ALL_TRANSACTIONS['P.Type'][idx]), str(ALL_TRANSACTIONS['Total'][idx]))

# Repeating above for Inventory excel file
if not os.path.isfile('Inventory.xlsx'):
    header_df = pd.DataFrame({'Name': [], 'Barcode': [], 'S.Price': [], 'P.Price': [], 'Quantity': [],
                              'Online_Price': [], 'Tax': []})
    header_df.to_excel('Inventory.xlsx', index=False)

INVENTORY_DF = pd.read_excel('Inventory.xlsx', ignore_index=True)

item_database.deleteData()

for idx, name in enumerate(list(INVENTORY_DF['Name'])):
    item_database.addData(name, str(INVENTORY_DF['Barcode'][idx]), str(INVENTORY_DF['P.Price'][idx]),
                          str(INVENTORY_DF['S.Price'][idx]), str(INVENTORY_DF['Quantity'][idx]),
                          str(INVENTORY_DF['Online_Price'][idx]), str(INVENTORY_DF['Tax'][idx]))

# Initializing cyclical iterator for online/offline label
ON_OFF_CYC = itertools.cycle('of')

# Open receipt.txt and empty it in case of future runs
open('receipt.txt', 'w').write('')

# Initializing a list which will encompass the items to which discount is added
discount_added = []


# --------------- Helper Functions --------------- #


def update_all_transaction_df():
    """will take in any modifications done to the excel file, and also add a tax column to it."""
    new_all_transactions_df = pd.read_excel('Transactions.xlsx', ignore_index=True)
    new_all_transactions_df['Total'] = pd.to_numeric(new_all_transactions_df['Total'], errors='coerce')

    # adding taxes column to be added into the excel file
    taxes = []

    for i in range(len(new_all_transactions_df)):
        if str(item_database.getTaxableFromNameAndSP(new_all_transactions_df['Name'][i],
                                                     new_all_transactions_df['S.Price'][i])) == 'T':
            t = Decimal(Decimal(new_all_transactions_df['S.Price'][i]) * Decimal(0.0825)).quantize(Decimal('.01'))
            taxes.append(t)
        elif str(new_all_transactions_df['Name'][i]) == 'Misc.':
            real_p = Decimal(Decimal(new_all_transactions_df['S.Price'][i]) / Decimal(1.0825)).quantize(Decimal('.01'))
            t = Decimal(Decimal(new_all_transactions_df['S.Price'][i]) - real_p).quantize(Decimal('.01'))
            taxes.append(t)
        else:
            taxes.append(Decimal(0.0))

    new_all_transactions_df['Tax'] = taxes
    new_all_transactions_df['Tax'] = pd.to_numeric(new_all_transactions_df['Tax'])

    return new_all_transactions_df


def update_inventory_df():
    """will take in any modifications done to the excel file"""
    new_inventory_df = pd.read('Inventory.xlsx')
    return new_inventory_df


def erase_previous_entry(entries):
    """sets entry widget to blank"""
    for entry in entries:
        entry.delete(0, 'end')


def click_on_barcode_entry():
    """currently, setting focus is not working, so I found a work-around to simply click the entry with
    the mouse."""
    win32api.SetCursorPos((320, 140))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 320, 140, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 320, 140, 0, 0)


def set_focus_on_entry(entry):
    """sets focus on a given entry"""
    entry.focus()
    return "break"


def display_item_database_table(item_list_frame):
    """displays the items table onto a tkinter table"""
    # fetching data from database
    items = item_database.getData()

    # creating tkinter table to display items in the item_database table
    TableModel()
    data = {}

    for i in range(len(items)):
        data['row' + str(i + 1)] = {'Name': items[i][0], 'Barcode': items[i][1],
                                    'P.Price': items[i][2], 'S.Price': items[i][3],
                                    'Quantity': items[i][4], 'Online $': items[i][5],
                                    'Tax': items[i][6]}

    table = TableCanvas(item_list_frame, data=data)
    table.show()


def display_all_transactions_database_table(item_list_frame):
    """displays the items table onto a tkinter table"""
    # fetching data from database
    items = all_transactions_database.getData()

    # creating tkinter table to display items in the item_database table
    TableModel()
    data = {}

    for i in range(len(items)):
        data['row' + str(i + 1)] = {'Name': items[i][0], 'S.Price': items[i][1],
                                    'Date': items[i][2], 'Payment Type': items[i][3],
                                    'Total': items[i][4]}

    table = TableCanvas(item_list_frame, data=data)
    table.show()


def get_tax_amount():
    """ Returns the tax amount in dollars of the current transactions."""
    transaction_items = transactions_database.getData()
    total_sale = Decimal(0.0)

    for i in range(len(transaction_items)):
        if str(item_database.getTaxableFromNameAndSP(str(transaction_items[i][0]), transaction_items[i][1])) == 'T':
            # setting precision length of decimal
            total_sale += Decimal(transaction_items[i][1]).quantize(Decimal('.01'))
        elif str(item_database.getTaxableFromNameAndOP(str(transaction_items[i][0]), transaction_items[i][1])) == 'T':
            # setting precision length of decimal
            total_sale += Decimal(transaction_items[i][1]).quantize(Decimal('.01'))

    return Decimal(Decimal(0.0825) * total_sale).quantize(Decimal('.01'))


def get_transactions_total_wout_tax():
    """ Returns transaction total without the tax."""
    transaction_items = transactions_database.getData()
    total_sale = Decimal(0.0)

    if len(transaction_items) > 0:
        for i in range(len(transaction_items)):
            # setting precision length of decimal
            total_sale += Decimal(transaction_items[i][1]).quantize(Decimal('.01'))

    return total_sale


def get_transactions_total():
    """simply addition of the above two function return values."""
    return Decimal(get_transactions_total_wout_tax() + get_tax_amount()).quantize(Decimal('.01'))


def show_transaction_table(frame, frame1):
    """displays the transactions table onto a tkinter table"""

    model = TableModel()
    transaction_items = transactions_database.getData()

    data = {}
    data1 = {}

    total_sale = get_transactions_total()

    for i in range(len(transaction_items)):
        data['row' + str(i + 1)] = {'Name': transaction_items[i][0], 'S.Price': transaction_items[i][1],
                                    'Date': transaction_items[i][2]}

        data1['row1'] = {'Total ($)': str(total_sale)}

    table1 = TableCanvas(frame1, data=data1, model=model)
    table = TableCanvas(frame, data=data, model=model)
    click_on_barcode_entry()
    table.show()
    table1.show()


def delete_pressed(frame, frame1):
    """gets rid of the temporary transaction"""
    transactions_database.deleteData()
    show_transaction_table(frame, frame1)


def print_receipt():
    """Prints the Receipt onto the given printer."""
    filename = "receipt.txt"
    if len(PRINTER_NAME) > 0:
        try:
            win32print.SetDefaultPrinter(PRINTER_NAME)
            win32api.ShellExecute(
                0,
                "printto",
                filename,
                '"%s"' % win32print.GetDefaultPrinter(),
                ".",
                0
            )
        except Exception as e:
            print("Something went wrong when trying to print:", str(e))


def print_option(barcodes):
    """Displays the option of whether you want to print a receipt at the end of the
    transaction."""
    root_tk_in = tk.Tk()
    root_tk_in.configure(bg=TK_INPUT_BG)
    root_tk_in.title("Print Option")
    canvas_in = tk.Canvas(root_tk_in, height=TK_INPUT_WIN_H, width=500, bg=TK_INPUT_BG)
    canvas_in.pack()

    # option label
    option_label = tk.Label(root_tk_in, text='Do you want to print a receipt?', bg=TK_INPUT_BG, fg=FG_LABELS_COLOR,
                            font=FONT)
    option_label.place(relx=0.1, rely=0.4, relheight=0.1, relwidth=0.8)
    # yes button
    yes_btn = tk.Button(root_tk_in, text='Yes', bg=YES_BTN, fg=FG_LABELS_COLOR, font=FONT,
                        command=lambda: [print_receipt(), root_tk_in.destroy(), done_btn_pressed(barcodes),
                                         update_inventory_df(),
                                         update_all_transaction_df()])
    yes_btn.place(relx=0.2, rely=0.55, relheight=0.1, relwidth=0.2)
    # no button
    no_btn = tk.Button(root_tk_in, text='No', bg=NO_BTN, fg=FG_LABELS_COLOR, font=FONT,
                       command=lambda: [root_tk_in.destroy(), done_btn_pressed(barcodes),
                                        update_inventory_df(),
                                        update_all_transaction_df()])
    no_btn.place(relx=0.6, rely=0.55, relheight=0.1, relwidth=0.2)
    no_btn.focus_force()

    root_tk_in.mainloop()


def done_btn_pressed(barcodes):
    """prints receipt.txt & deletes the transactions database table,
    so it can be empty for the next transaction event"""

    filename = "receipt.txt"

    transaction_items = transactions_database.getData()
    for idx, t in enumerate(list(transaction_items)):
        if idx != len(list(transaction_items)) - 1:
            all_transactions_database.addData(t[0], t[1], t[2], t[3], '')
        else:
            if len(discount_added) == 0:
                all_transactions_database.addData(t[0], t[1], t[2], t[3], str(get_transactions_total()))
            else:
                discounted_total = Decimal(get_transactions_total() - (
                            Decimal(discount_added[0]) * Decimal(0.01) * get_transactions_total())).quantize(
                    Decimal('.01'))
                all_transactions_database.addData(t[0], t[1], t[2], t[3], str(discounted_total))

    decrease_qtn(barcodes)
    barcodes.clear()

    transactions_database.deleteData()
    inv_df = pd.read_excel('Inventory.xlsx')

    # Don't want purchase price to be shown in the google sheets
    new_invn = pd.DataFrame()
    new_invn['Barcode'] = inv_df['Barcode']
    new_invn['Name'] = inv_df['Name']
    new_invn['S.Price'] = inv_df['S.Price']
    new_invn['Quantity'] = inv_df['Quantity']

    WKS.set_dataframe(new_invn, (1, 1))

    trans_df = pd.read_excel("Transactions.xlsx")
    WKS_T.set_dataframe(trans_df, (1, 1))

    # clear the receipt file for next transaction
    open(filename, 'w').write('')


def update_receipt_text():
    receipt_file = open("receipt.txt", "r+")

    present_lines = receipt_file.readlines()

    receipt_file.close()

    transaction_items = transactions_database.getData()
    dup_list_of_item_names = [t[0] for t in transaction_items]
    list_of_sp = [t[1] for t in transaction_items]
    list_of_qtns = []

    list_of_item_names = list(set(dup_list_of_item_names))

    for i in list_of_item_names:
        list_of_qtns.append(dup_list_of_item_names.count(i))

    header = "               LIQUOR PALACE\n\t6965 Harwin Dr\n\t 346 980 8859\n\n"

    subtotal = Decimal(0.0)

    for idx, item in enumerate(list_of_item_names):
        header += str(item) + "     " + str(list_of_qtns[idx]) + "     $" + str(list_of_sp[idx]) + "\n"
        subtotal += Decimal(Decimal(list_of_sp[idx]) * Decimal(list_of_qtns[idx])).quantize(Decimal('.01'))

    tax = Decimal(Decimal(0.0825) * subtotal).quantize(Decimal('.01'))
    total = Decimal(subtotal + tax).quantize(Decimal('.01'))
    header += "\nSUBTOTAL" + "\t$" + str(subtotal) + "\n" + "TAX" + "\t\t$" + str(tax) + "\n" + "TOTAL" + "\t\t$" + \
              str(total) + "\n"

    for line in present_lines:
        header += line

    open('receipt.txt', 'w').write(header)


def show_monthly_analysis(frame):
    """displays monthly revenue bar graph"""
    # Adding the revenue bar graph
    fig = Figure(figsize=(5, 5), dpi=80)
    subplot = fig.add_subplot(111)
    updated_at_df = pd.read_excel('Transactions.xlsx')
    updated_at_df['Revenue'] = updated_at_df['S.Price']
    updated_at_df['Month'] = updated_at_df['Date'].str[5:7]
    updated_at_df['Month'] = updated_at_df['Month'].astype('int32')
    monthly_revs = updated_at_df.groupby('Month').sum()
    months = [x for x in updated_at_df['Month']]
    non_rep_months = []
    for month in months:
        if month not in non_rep_months:
            non_rep_months.append(month)
    # plotting the bar graph
    subplot.set_xticks(non_rep_months)
    subplot.set_xlabel('Month Number')
    subplot.set_ylabel('Sale ($)')
    subplot.set_title('Total Sale Per Month for the Year')
    subplot.bar(non_rep_months, monthly_revs['Revenue'], color="#eb6e34")

    # displaying the bar graph onto tkinter window
    canvas = FigureCanvasTkAgg(fig, frame)
    canvas.draw()
    canvas.get_tk_widget().place(relx=0.05, rely=0.3, relheight=0.5, relwidth=0.4)


def show_sale_frequency_analysis(frame):
    """displays sales frequency bar graph"""
    updated_at_df = pd.read_excel('Transactions.xlsx')
    # Adding the sale frequency bar graph
    fig1 = Figure(figsize=(5, 5), dpi=80)
    subplot1 = fig1.add_subplot(111)

    # 1st - making a list that has the data of the name of item and its sale frequency
    item_names = updated_at_df['Name']
    item_names_and_freq = []
    for name in item_names:
        count = updated_at_df['Name'] \
            .where(updated_at_df['Name'] == name).count()
        if [name, count] not in item_names_and_freq:
            item_names_and_freq.append([name, count])
    # 2nd - sorting the list by greatest to least sale frequency
    item_names_and_freq.sort(key=lambda x: x[1], reverse=True)
    # plotting a bar graph
    x_var = [n[0] for n in item_names_and_freq]
    y_var = [f[1] for f in item_names_and_freq]
    if len(x_var) > 10:  # capping the max number of items to be 10
        x_var = x_var[:10]
        y_var = y_var[:10]
    subplot1.bar(x_var, y_var, color="#eb6e34")
    subplot1.set_title("Top Selling Items (up to 10)")
    subplot1.set_xlabel("Item Name")
    subplot1.set_xticklabels([n[0:7] for n in item_names])
    subplot1.set_ylabel("Sale Frequency")

    # displaying the bar graph onto tkinter window
    canvas1 = FigureCanvasTkAgg(fig1, frame)
    canvas1.draw()
    canvas1.get_tk_widget().place(relx=0.55, rely=0.3, relheight=0.5, relwidth=0.4)


# Helper functions referenced in pages (to add/show/update items, transactions into databases, etc.)
def add_item_to_item_database(name, barcode, pp, sp, qtn, op, tax, text):
    """takes in necessary parameters and adds item into the item_database table"""
    if (barcode,) in item_database.getBarcodes():
        text.set("Item is already in your inventory :)")  # sets the text of message label
    else:
        if tax == '0':
            tax = 'T'
        else:
            tax = 'N'

        item_database.addData(name, barcode, pp, sp, qtn, op, tax)
        text.set("Item was added :)")  # sets the text of message label


def add_item_to_transactions_databases(name, sp, date, op, payment_type='CREDIT'):
    """takes in necessary parameters and adds item into transactions table"""
    if name is not None:
        next(ON_OFF_CYC)
        if next(ON_OFF_CYC) == 'o':
            transactions_database.addData(name, op, date, payment_type)
        else:
            transactions_database.addData(name, sp, date, payment_type)


def update_name(new_name, barcode, text):
    """takes in necessary parameters and updates the name of the item based on the barcode"""
    if (barcode,) in item_database.getBarcodes():
        item_database.updateName(new_name, barcode)
        text.set("Item was updated :)")  # sets the text of the message label
    else:
        text.set("Item is not in your inventory :(")  # sets the text of the message label


def update_pp(new_pp, barcode, text):
    """takes in necessary parameters and updates the pp of the item based on the barcode"""
    if (barcode,) in item_database.getBarcodes():
        item_database.updatePurchasePrice(new_pp, barcode)
        text.set("Item was updated :)")
    else:
        text.set("Item is not in your inventory :(")


def update_sp(new_sp, barcode, text):
    """takes in necessary parameters and updates the sp of the item based on the barcode"""
    if (barcode,) in item_database.getBarcodes():
        item_database.updateSalePrice(new_sp, barcode)
        text.set("Item was updated :)")  # sets text of message label
    else:
        text.set("Item is not in your inventory :(")  # sets text of message label


def update_qtn(new_qtn, barcode, text):
    """takes in necessary parameters and updates the qtn of the item based on the barcode"""
    if (barcode,) in item_database.getBarcodes():
        item_database.updateQuantity(new_qtn, barcode)
        text.set("Item was updated :)")  # sets text of message label
    else:
        text.set("Item is not in your inventory :(")  # sets text of message label


def update_op(new_op, barcode, text):
    """takes in necessary parameters and updates the qtn of the item based on the barcode"""
    if (barcode,) in item_database.getBarcodes():
        item_database.updateOP(new_op, barcode)
        text.set("Item was updated :)")  # sets text of message label
    else:
        text.set("Item is not in your inventory :(")  # sets text of message label


def decrease_qtn(barcodes):
    """takes in barcode and decrements quantity of that item by 1--used when committing transactions"""
    for b in barcodes:
        item_database.decreaseQuantityByOne(b)


def get_return_value(total, cash_given):
    """show how much money you owe to customer after they give you a bill."""
    return Decimal(Decimal(total) - Decimal(cash_given)).quantize(Decimal('.01'))


def get_return_value_with_discount(tot_wout_tax, discount):
    """show money to give or get on a discounted transaction."""
    discount_amount = Decimal(Decimal(tot_wout_tax) * Decimal(discount) * Decimal(0.01)).quantize(Decimal('.01'))
    return_val = Decimal(Decimal(tot_wout_tax) - discount_amount + Decimal(get_tax_amount())).quantize(Decimal('.01'))

    return return_val


def show_after_discount(tot_wout_tax, discount, root_win):
    """amount owed after discount."""
    discount_added.append(discount)

    receipt_file = open('receipt.txt', 'w+')

    discount_amount = Decimal(Decimal(tot_wout_tax) * Decimal(discount) * Decimal(0.01)).quantize(Decimal('.01'))
    return_val = Decimal(Decimal(tot_wout_tax) - discount_amount + Decimal(get_tax_amount())).quantize(Decimal('.01'))

    return_label = tk.Label(root_win, text="DUE:\n" + str(abs(return_val)), bg=TK_INPUT_BG, fg=FG_LABELS_COLOR,
                            font=FONT)
    return_label.place(relx=0.3, rely=0.5, relheight=0.15, relwidth=0.4)

    receipt_line = "\nDISCOUNT " + str(discount) + "%" + "\t-$" + str(discount_amount)
    receipt_line += "\nBALANCE:\t$" + str(return_val)

    receipt_file.write(receipt_line)
    receipt_file.close()


def change_payment_type(p_type):
    """changing between CREDIT or CASH payment type"""
    transactions_database.updatePaymentType(str(p_type))


def show_return(total, cash_given, root_win):
    """shows how much money you owe to customer after they give you a bill."""
    receipt_file = open('receipt.txt', 'r+')

    present_lines = receipt_file.readlines()

    return_val = get_return_value(total, cash_given)
    give_or_get = ''
    if return_val < 0:
        give_or_get = 'Give:\n$'
    else:
        give_or_get = 'Get:\n$'

    return_label = tk.Label(root_win, text=give_or_get + str(abs(return_val)), bg=TK_INPUT_BG, fg=FG_LABELS_COLOR,
                            font=FONT)
    return_label.place(relx=0.28, rely=0.84, relheight=0.15, relwidth=0.4)

    receipt_line = ''
    if len(present_lines) > 0:
        for line in present_lines:
            receipt_line += line

    receipt_line += "\nCASH:\t\t$" + str(cash_given)
    receipt_line += "\nBALANCE:\t$" + str(abs(return_val))

    open('receipt.txt', 'w').write(receipt_line)

    change_payment_type('CASH')


def get_misc_tot(p, q):
    """adds tax to misc. item price you add."""
    return Decimal(Decimal(p) * Decimal(q)).quantize(Decimal('.01'))


def get_misc_tot_w_tax(p, q):
    tot = Decimal(Decimal(p) * Decimal(q))
    tax = Decimal(Decimal(0.0825) * Decimal(tot))
    tot = Decimal(tot + tax).quantize(Decimal('.01'))
    return tot


def offline_label(frame):
    """places a label on top to let you know that the transaction being done is offline,
    and will account for the offline sale prices of the items."""
    offline_l = tk.Label(frame, text='Offline', bg=OFFLINE_IND_COLOR, fg=FG_LABELS_COLOR, font=('Courier', 14, 'bold'))
    offline_l.place(relx=0.1, rely=0.0, relheight=0.1, relwidth=0.8)


def online_transaction(main_frame):
    """places a label on top to let you know that the transaction being done is online,
    and will account for the online sale prices of the items."""
    online_label = tk.Label(main_frame, text='Online', bg=ONLINE_IND_COLOR, fg=FG_LABELS_COLOR, font=FONT)
    next_on_off = next(ON_OFF_CYC)
    if next_on_off == 'o':
        # online label
        online_label.place(relx=0.1, rely=0.0, relheight=0.1, relwidth=0.8)
    else:
        offline_label(main_frame)


def misc_window(f, f1):
    root_tk_in = tk.Tk()
    root_tk_in.configure(bg=TK_INPUT_BG)
    root_tk_in.title("Misc. Window")
    canvas_in = tk.Canvas(root_tk_in, height=TK_INPUT_WIN_H, width=TK_INPUT_WIN_W, bg=TK_INPUT_BG)
    canvas_in.pack()

    # dollar sign label
    dollar_label = tk.Label(root_tk_in, text='$', bg=TK_INPUT_BG, fg=FG_LABELS_COLOR, font=FONT)
    dollar_label.place(relx=0.25, rely=0.1, relheight=0.15, relwidth=0.05)
    # price entry
    price_entry = tk.Entry(root_tk_in, bg=TK_INPUT_BG,
                           fg=FG_LABELS_COLOR, font=FONT)
    price_entry.place(relx=0.32, rely=0.1, relheight=0.15, relwidth=0.4)
    price_entry.focus_force()
    # quantity label
    quantity_label = tk.Label(root_tk_in, text='Qtn:', bg=TK_INPUT_BG, fg=FG_LABELS_COLOR, font=FONT)
    quantity_label.place(relx=0.05, rely=0.3, relheight=0.15, relwidth=0.4)
    # quantity entry
    quantity_entry = tk.Entry(root_tk_in, bg=TK_INPUT_BG, fg=FG_LABELS_COLOR, font=FONT)
    quantity_entry.place(relx=0.4, rely=0.3, relheight=0.15, relwidth=0.32)

    quantity_entry.bind('<Return>', lambda event: [
        add_item_to_transactions_databases('Misc.', str(get_misc_tot_w_tax(price_entry.get(), quantity_entry.get())),
                                           str(datetime.datetime.today()).split(' ')[0], 0.0),
        show_transaction_table(f, f1), root_tk_in.destroy()])

    root_tk_in.mainloop()


def discount_window():
    root_tk_in = tk.Tk()
    root_tk_in.configure(bg=TK_INPUT_BG)
    root_tk_in.title("Discount Window")
    canvas_in = tk.Canvas(root_tk_in, height=360, width=TK_INPUT_WIN_W, bg=TK_INPUT_BG)
    canvas_in.pack()

    total_wout_tax = get_transactions_total_wout_tax()

    # transaction total without Tax label
    tot_label = tk.Label(root_tk_in, text="$" + str(total_wout_tax), bg=TK_INPUT_BG,
                         fg=FG_LABELS_COLOR, font=FONT)
    tot_label.place(relx=0.3, rely=0.1, relheight=0.15, relwidth=0.4)

    # - label
    minus_label = tk.Label(root_tk_in, text="-", bg=TK_INPUT_BG, fg=FG_LABELS_COLOR, font=FONT)
    minus_label.place(relx=0.25, rely=0.3, relheight=0.15, relwidth=0.1)
    # discount percentage entry
    discount_entry = tk.Entry(root_tk_in, bg=TK_INPUT_BG, fg=FG_LABELS_COLOR, font=FONT)
    discount_entry.place(relx=0.36, rely=0.3, relheight=0.15, relwidth=0.28)
    discount_entry.focus_force()
    # % label
    percent_label = tk.Label(root_tk_in, text='%', bg=TK_INPUT_BG, fg=FG_LABELS_COLOR, font=FONT)
    percent_label.place(relx=0.64, rely=0.3, relheight=0.15, relwidth=0.1)

    # cash given entry
    cash_given_entry = tk.Entry(root_tk_in, bg=TK_INPUT_BG, fg=FG_LABELS_COLOR, font=FONT)
    cash_given_entry.place(relx=0.36, rely=0.7, relheight=0.15, relwidth=0.29)

    discount_entry.bind('<Return>', lambda event: [show_after_discount(total_wout_tax, discount_entry.get(),
                                                                       root_tk_in)])

    cash_given_entry.bind('<Return>', lambda event: [show_return(get_return_value_with_discount(total_wout_tax,
                                                                                                discount_entry.get()),
                                                                 cash_given_entry.get(), root_tk_in)])

    root_tk_in.mainloop()


def return_window():
    root_tk_in = tk.Tk()
    root_tk_in.title("Cash Return Window")
    canvas_in = tk.Canvas(root_tk_in, height=TK_INPUT_WIN_H, width=TK_INPUT_WIN_W, bg=TK_INPUT_BG)
    canvas_in.pack()

    # transaction total entry (for discount)
    tot_entry = tk.Entry(root_tk_in, bg=TK_INPUT_BG,
                         fg=FG_LABELS_COLOR, font=FONT)
    tot_entry.insert('end', str(get_transactions_total()))
    tot_entry.place(relx=0.3, rely=0.1, relheight=0.15, relwidth=0.4)

    # customer cash label
    minus_label = tk.Label(root_tk_in, text="-", bg=TK_INPUT_BG, fg=FG_LABELS_COLOR, font=FONT)
    minus_label.place(relx=0.25, rely=0.3, relheight=0.15, relwidth=0.1)
    # customer cash entry
    cash_given_entry = tk.Entry(root_tk_in, bg=TK_INPUT_BG, fg=FG_LABELS_COLOR, font=FONT)
    cash_given_entry.place(relx=0.36, rely=0.3, relheight=0.15, relwidth=0.29)
    cash_given_entry.focus_force()

    cash_given_entry.bind('<Return>', lambda event: [show_return(tot_entry.get(), cash_given_entry.get(), root_tk_in)])

    root_tk_in.mainloop()


def set_v(var, text):
    var.set(text)


# driver class for the app which will stack frames on the top when they are called
class InventoryApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)
        container.pack(fill='both', expand=True)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        self.frames = {}

        # all the pages in the app:
        pages = (MainPage, InventoryPage, AddInventoryPage, SeeItemsPage, UpdatePage, TransactionPage, AnalysisPage)

        for F in pages:
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame(MainPage)

    def post_update(self):
        pass

    def show_frame(self, cont):
        """stacks frame on the top"""
        frame = self.frames[cont]
        frame.tkraise()

        try:
            frame.post_update()
        except AttributeError:
            pass


# Main Page view
class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        self.Frame = tk.Frame.__init__(self, parent)

        # Canvas
        canvas = tk.Canvas(self, height=700, width=800)
        canvas.pack()

        # Background Label (i.e the image in the background)
        self.bgImg = tk.PhotoImage(file='background.png')
        bg_label = tk.Label(self, image=self.bgImg)
        bg_label.place(relheight=1, relwidth=1, anchor='nw')

        # Adding Buttons
        # Adding a frame in the middle
        frame = tk.Frame(self, bg=BACKGROUND_FRAME_COLOR)
        frame.place(relx=0.125, rely=0.2, relheight=0.5, relwidth=0.75)
        # Adding inventory button
        self.inventory_btn_image = tk.PhotoImage(file='supplier.png')
        inventory_btn = tk.Button(frame, padx=24, image=self.inventory_btn_image,
                                  text="Access/Update" + "\n" + "Inventory", bg=BUTTON_AND_LABEL_COLOR,
                                  font=FONT, command=lambda: controller.show_frame(InventoryPage))
        inventory_btn.place(relx=0.02, rely=0.05, relheight=0.9, relwidth=0.4)
        # Adding transaction button
        self.transaction_btn_image = tk.PhotoImage(file='card-machine.png')
        transaction_btn = tk.Button(frame, image=self.transaction_btn_image,
                                    bg=BUTTON_AND_LABEL_COLOR, command=lambda: [controller.show_frame(TransactionPage),
                                                                                discount_added.clear()])
        transaction_btn.place(relx=0.58, rely=0.05, relheight=0.9, relwidth=0.4)
        # Adding see all transactions button
        self.see_trans_img = tk.PhotoImage(file='transactions_file.png')
        see_trans_btn = tk.Button(self, image=self.see_trans_img, bg='#a2f78b',
                                  command=lambda: os.startfile('Transactions.xlsx'))
        see_trans_btn.place(relx=0.9, rely=0.25, relheight=0.1, relwidth=0.1)

        # Adding see all inventory button
        self.see_inv_img = tk.PhotoImage(file='inventory_pic.png')
        see_inv_btn = tk.Button(self, image=self.see_inv_img, bg='#bdd6ff',
                                command=lambda: os.startfile('Inventory.xlsx'))
        see_inv_btn.place(relx=0.9, rely=0.35, relheight=0.1, relwidth=0.1)

        # Adding Show Monthly Revenue button
        analysis_frame = tk.Frame(self, bg=BACKGROUND_FRAME_COLOR)
        analysis_frame.place(relx=0.25, rely=0.7, relheight=0.15, relwidth=0.5)
        analysis_btn = tk.Button(analysis_frame, text='Show Analysis', bg=BUTTON_AND_LABEL_COLOR,
                                 font=FONT, command=lambda: [update_all_transaction_df(), update_inventory_df(),
                                                             controller.show_frame(AnalysisPage)])
        analysis_btn.place(relx=0.25, rely=0.2, relheight=0.5, relwidth=0.5)

    def post_update(self):
        pass


# Inventory Page view
class InventoryPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Background Label (i.e. background image)
        self.bgImg = tk.PhotoImage(file='background.png')
        bg_label = tk.Label(self, image=self.bgImg)
        bg_label.place(relheight=1, relwidth=1, anchor='nw')

        # frame on top for all the buttons
        top_frame = tk.Frame(self, bg=BACKGROUND_FRAME_COLOR)
        top_frame.place(relx=0.1, rely=0.5, relheight=0.1, relwidth=0.8)

        # adding 'see' button
        see_btn = tk.Button(top_frame, bg=BUTTON_AND_LABEL_COLOR, text='SEE', font=FONT,
                            command=lambda: controller.show_frame(SeeItemsPage))
        see_btn.place(relx=0.02, rely=0.25, relheight=0.5, relwidth=0.8 / 3)

        # adding 'add' button
        add_btn = tk.Button(top_frame, bg=BUTTON_AND_LABEL_COLOR, text='ADD', font=FONT,
                            command=lambda: controller.show_frame(AddInventoryPage))
        add_btn.place(relx=0.8 / 3 + 0.1, rely=0.25, relheight=0.5, relwidth=0.8 / 3)

        # adding 'update' button
        update_btn = tk.Button(top_frame, bg=BUTTON_AND_LABEL_COLOR, text='UPDATE', font=FONT,
                               command=lambda: controller.show_frame(UpdatePage))
        update_btn.place(relx=(0.8 / 3) * 2 + 0.175, rely=0.25, relheight=0.5, relwidth=0.8 / 3)

        # Adding a back button
        back_btn_frame = tk.Frame(self, bg=BACKGROUND_FRAME_COLOR)
        back_btn_frame.place(relx=0.4, rely=0.85, relheight=0.1, relwidth=0.2)
        back_btn = tk.Button(back_btn_frame, bg=BACK_BUTTON_COLOR, font=FONT, text='Back',
                             command=lambda: controller.show_frame(MainPage))
        back_btn.place(relx=0.25, rely=0.3, relheight=0.5, relwidth=0.5)

    def post_update(self):
        pass


# AddInventoryPage view
class AddInventoryPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Background Label
        self.bgImg = tk.PhotoImage(file='background.png')
        bg_label = tk.Label(self, image=self.bgImg)
        bg_label.place(relheight=1, relwidth=1, anchor='nw')

        # Adding Item Frame
        frame = tk.Frame(self, bg=BACKGROUND_FRAME_COLOR)
        frame.place(relx=0.1, rely=0.1, relheight=0.8, relwidth=0.8)

        # Adding Entries
        # name entry
        name_entry = tk.Entry(frame, font=FONT, bg=ENTRY_COLOR)
        name_entry.focus()
        name_entry_label = tk.Label(frame, bg=BUTTON_AND_LABEL_COLOR, font=FONT, text='Enter Name')
        name_entry.place(relx=0.45, rely=0.05, relheight=0.1, relwidth=0.3)
        name_entry_label.place(relx=0.25, rely=0.05, relheight=0.1, relwidth=0.2)
        # barcode entry
        barcode_entry = tk.Entry(frame, font=FONT, bg=ENTRY_COLOR)
        barcode_entry_label = tk.Label(frame, bg=BUTTON_AND_LABEL_COLOR, font=FONT, text='Barcode')
        barcode_entry.place(relx=0.45, rely=0.17, relheight=0.1, relwidth=0.3)
        barcode_entry_label.place(relx=0.25, rely=0.17, relheight=0.1, relwidth=0.2)
        # purchase price
        pp_entry = tk.Entry(frame, font=FONT, bg=ENTRY_COLOR)
        pp_entry_label = tk.Label(frame, bg=BUTTON_AND_LABEL_COLOR, text='P.Price', font=FONT, )
        pp_entry.place(relx=0.45, rely=0.29, relheight=0.1, relwidth=0.3)
        pp_entry_label.place(relx=0.25, rely=0.29, relheight=0.1, relwidth=0.2)
        # sale price
        sp_entry = tk.Entry(frame, font=FONT, bg=ENTRY_COLOR)
        sp_entry_label = tk.Label(frame, bg=BUTTON_AND_LABEL_COLOR, font=FONT, text='S.Price')
        sp_entry.place(relx=0.45, rely=0.41, relheight=0.1, relwidth=0.3)
        sp_entry_label.place(relx=0.25, rely=0.41, relheight=0.1, relwidth=0.2)
        # quantity
        qtn_entry = tk.Entry(frame, font=FONT, bg=ENTRY_COLOR)
        qtn_entry_label = tk.Label(frame, bg=BUTTON_AND_LABEL_COLOR, font=FONT, text='Quantity')
        qtn_entry.place(relx=0.45, rely=0.53, relheight=0.1, relwidth=0.3)
        qtn_entry_label.place(relx=0.25, rely=0.53, relheight=0.1, relwidth=0.2)
        # online price
        online_entry = tk.Entry(frame, font=FONT, bg=ENTRY_COLOR)
        online_label = tk.Label(frame, bg=BUTTON_AND_LABEL_COLOR, font=FONT, text='Online $')
        online_entry.place(relx=0.45, rely=0.65, relheight=0.1, relwidth=0.3)
        online_label.place(relx=0.25, rely=0.65, relheight=0.1, relwidth=0.2)
        # tax, non-tax radio buttons
        MODES = [
            ("Tax", "0"),
            ("Non-Tax", "1")
        ]

        v = tk.StringVar()
        v.set("0")  # initialize

        for text, mode in MODES:
            b = tk.Radiobutton(frame, text=text, bg=TK_INPUT_BG, font=('Courier', 10, 'bold'),
                               fg='#ff3b3b', variable=v, value=mode, command=lambda: [set_v(v, v.get())])
            b.pack(anchor='w')

        # setting text of message (will appear when item is added)
        self.text = tk.StringVar()
        self.text.set("")
        # message label
        message_label = tk.Label(frame, bg=BACKGROUND_FRAME_COLOR, font=FONT, fg='#fffafa', textvariable=self.text)
        message_label.place(relx=0.1, rely=0.90, relheight=0.05, relwidth=0.8)

        # Add Item Button
        add_item_btn = tk.Button(frame, bg='#e8eb34', font=FONT, text='ADD', command=lambda: [
            add_item_to_item_database(name_entry.get(), int(barcode_entry.get()), pp_entry.get(),
                                      sp_entry.get(), int(qtn_entry.get()), online_entry.get(), v.get(), self.text),
            erase_previous_entry([name_entry, barcode_entry, sp_entry, pp_entry, qtn_entry, online_entry]),
            update_all_transaction_df(), update_inventory_df()])
        add_item_btn.place(relx=0.45, rely=0.8, relheight=0.1, relwidth=0.1)

        # Add Back Button
        back_btn_frame = tk.Frame(self, bg=BACKGROUND_FRAME_COLOR)
        back_btn_frame.place(relx=0.4, rely=0.85, relheight=0.1, relwidth=0.2)
        back_btn = tk.Button(back_btn_frame, bg=BACK_BUTTON_COLOR, font=FONT, text='Back',
                             command=lambda: controller.show_frame(InventoryPage))
        back_btn.place(relx=0.25, rely=0.3, relheight=0.5, relwidth=0.5)

    def post_update(self):
        pass


# SeeItemsPage view
class SeeItemsPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Background Label
        self.bgImg = tk.PhotoImage(file='background.png')
        bg_label = tk.Label(self, image=self.bgImg)
        bg_label.place(relheight=1, relwidth=1, anchor='nw')

        # new frame to see data
        self.itemsListFrame = tk.Frame(self, bg=BACKGROUND_FRAME_COLOR)
        self.itemsListFrame.place(relx=0.15, rely=0.2, relheight=0.65, relwidth=0.7)

        # displaying table
        display_item_database_table(self.itemsListFrame)

        # Add Back Button
        back_btn_frame = tk.Frame(self, bg=BACKGROUND_FRAME_COLOR)
        back_btn_frame.place(relx=0.4, rely=0.85, relheight=0.1, relwidth=0.2)
        back_btn = tk.Button(back_btn_frame, bg=BACK_BUTTON_COLOR, font=FONT, text='Back',
                             command=lambda: controller.show_frame(InventoryPage))
        back_btn.place(relx=0.25, rely=0.3, relheight=0.5, relwidth=0.5)

    def post_update(self):
        """this helps the updated table to be displayed after multiple calls to the frame in the
        same run event"""
        display_item_database_table(self.itemsListFrame)


# UpdatePage view
class UpdatePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Background Label
        self.bgImg = tk.PhotoImage(file='background.png')
        bg_label = tk.Label(self, image=self.bgImg)
        bg_label.place(relheight=1, relwidth=1, anchor='nw')

        # Adding a frame in the middle
        frame = tk.Frame(self, bg=BACKGROUND_FRAME_COLOR)
        frame.place(relx=0.2, rely=0.2, relheight=0.7, relwidth=0.6)

        # Adding entries and labels for barcode and new name
        # barcode
        self.enter_barcode_entry = tk.Entry(frame, bg=ENTRY_COLOR, font=FONT)
        self.enter_barcode_entry.focus()
        enter_barcode_entry_label = tk.Label(frame, bg=BUTTON_AND_LABEL_COLOR, font=FONT,
                                             text='Enter Barcode')
        enter_barcode_entry_label.place(relx=0.1, rely=0.1, relheight=0.1, relwidth=0.4)
        self.enter_barcode_entry.place(relx=0.1, rely=0.2, relheight=0.1, relwidth=0.4)
        # new name
        name_var = tk.StringVar()
        enter_name_entry = tk.Entry(frame, bg=ENTRY_COLOR, font=FONT, textvariable=name_var)
        enter_name_entry_label = tk.Label(frame, bg=BUTTON_AND_LABEL_COLOR, font=FONT,
                                          text='Enter New Name')
        enter_name_entry_label.place(relx=0.5, rely=0.1, relheight=0.1, relwidth=0.4)
        enter_name_entry.place(relx=0.5, rely=0.2, relheight=0.1, relwidth=0.4)
        # new pp
        pp_var = tk.StringVar()
        enter_pp_entry = tk.Entry(frame, bg=ENTRY_COLOR, font=FONT, textvariable=pp_var)
        enter_pp_entry_label = tk.Label(frame, bg=BUTTON_AND_LABEL_COLOR, font=FONT, text='New P.Price')
        enter_pp_entry_label.place(relx=0.1, rely=0.3, relheight=0.1, relwidth=0.4)
        enter_pp_entry.place(relx=0.1, rely=0.4, relheight=0.1, relwidth=0.4)
        # new sp
        sp_var = tk.StringVar()
        enter_sp_entry = tk.Entry(frame, bg=ENTRY_COLOR, font=FONT, textvariable=sp_var)
        enter_sp_entry_label = tk.Label(frame, bg=BUTTON_AND_LABEL_COLOR, font=FONT,
                                        text='New S.Price')
        enter_sp_entry_label.place(relx=0.5, rely=0.3, relheight=0.1, relwidth=0.4)
        enter_sp_entry.place(relx=0.5, rely=0.4, relheight=0.1, relwidth=0.4)
        # new qtn
        qtn_var = tk.StringVar()
        enter_qtn_entry = tk.Entry(frame, bg=ENTRY_COLOR, font=FONT, textvariable=qtn_var)
        enter_qtn_entry_label = tk.Label(frame, bg=BUTTON_AND_LABEL_COLOR, font=FONT,
                                         text='New Quantity')
        enter_qtn_entry_label.place(relx=0.1, rely=0.5, relheight=0.1, relwidth=0.4)
        enter_qtn_entry.place(relx=0.1, rely=0.6, relheight=0.1, relwidth=0.4)
        # new op
        op_var = tk.StringVar()
        enter_op_entry = tk.Entry(frame, bg=ENTRY_COLOR, font=FONT, textvariable=op_var)
        enter_op_entry_label = tk.Label(frame, bg=BUTTON_AND_LABEL_COLOR, font=FONT, text='New O.Price')
        enter_op_entry_label.place(relx=0.5, rely=0.5, relheight=0.1, relwidth=0.4)
        enter_op_entry.place(relx=0.5, rely=0.6, relheight=0.1, relwidth=0.4)

        # on enter (barcode entry)
        self.enter_barcode_entry.bind('<Return>', lambda event: [
            name_var.set(item_database.getNameFromBarcode(int(self.enter_barcode_entry.get()))),
            pp_var.set(item_database.getPPFromBarcode(int(self.enter_barcode_entry.get()))),
            sp_var.set(item_database.getSalePriceFromBarcode(int(self.enter_barcode_entry.get()))),
            qtn_var.set(item_database.getQtnFromBarcode(int(self.enter_barcode_entry.get()))),
            op_var.set(item_database.getOPFromBarcode(int(self.enter_barcode_entry.get())))
        ])

        # setting text
        self.text = tk.StringVar()
        self.text.set("")
        # message label
        message_label = tk.Label(frame, bg=BACKGROUND_FRAME_COLOR, font=FONT, fg='#fffafa',
                                 textvariable=self.text)
        message_label.place(relx=0.1, rely=0.72, relheight=0.05, relwidth=0.8)

        # updating name button
        update_btn = tk.Button(frame, bg='#e8eb34', font=FONT, text='Update',
                               command=lambda: [update_name(enter_name_entry.get(),
                                                            int(self.enter_barcode_entry.get()), self.text),
                                                update_pp(enter_pp_entry.get(), int(self.enter_barcode_entry.get()),
                                                          self.text),
                                                update_sp(enter_sp_entry.get(), int(self.enter_barcode_entry.get()),
                                                          self.text),
                                                update_qtn(enter_qtn_entry.get(), int(self.enter_barcode_entry.get()),
                                                           self.text),
                                                update_op(enter_op_entry.get(), int(self.enter_barcode_entry.get()),
                                                          self.text),
                                                erase_previous_entry([self.enter_barcode_entry,
                                                                      enter_name_entry, enter_pp_entry, enter_sp_entry,
                                                                      enter_qtn_entry])])
        update_btn.place(relx=0.35, rely=0.8, relheight=0.1, relwidth=0.3)

        # Add Back Button
        back_btn_frame = tk.Frame(self, bg=BACKGROUND_FRAME_COLOR)
        back_btn_frame.place(relx=0.4, rely=0.85, relheight=0.1, relwidth=0.2)
        back_btn = tk.Button(back_btn_frame, bg='#d93027', font=('Courier', 15, 'bold'), text='Back',
                             command=lambda: controller.show_frame(InventoryPage))
        back_btn.place(relx=0.25, rely=0.3, relheight=0.5, relwidth=0.5)

    def post_update(self):
        self.enter_barcode_entry.focus()


# TransactionPage view
class TransactionPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Before populating the database, the data already present needs to be deleted
        transactions_database.deleteData()

        # Background Label
        self.bgImg = tk.PhotoImage(file='background.png')
        bg_label = tk.Label(self, image=self.bgImg)
        bg_label.place(relheight=1, relwidth=1, anchor='nw')

        # Adding a frame for the barcode entry
        self.barcodeFrame = tk.Frame(self, bg=BACKGROUND_FRAME_COLOR)
        self.barcodeFrame.place(relx=0.1, rely=0.1, relheight=0.15, relwidth=0.8)

        # Scan Barcode Label
        scan_label = tk.Label(self.barcodeFrame, text='Scan Barcode', bg=BACKGROUND_FRAME_COLOR, font=FONT,
                              fg='#fffafa')
        scan_label.place(relx=0.15, rely=0.1, relheight=0.14, relwidth=0.7)

        # Barcode Entry
        self.barcodeEntry = tk.Entry(self.barcodeFrame, bg=ENTRY_COLOR, font=FONT)
        self.barcodeEntry.place(relx=0.15, rely=0.3, relheight=0.4, relwidth=0.7)

        # Table Frame (to view transactions)
        self.tb_frame = tk.Frame(self, bg=BACKGROUND_FRAME_COLOR)
        self.tb_frame.place(relx=0.1, rely=0.3, relheight=0.6, relwidth=0.6)
        # Table Frame (to view total bill)
        self.tb_frame_1 = tk.Frame(self, bg=BACKGROUND_FRAME_COLOR)
        self.tb_frame_1.place(relx=0.7, rely=0.3, relheight=0.6, relwidth=0.2)

        barcodes = []

        # Adding an Enter button
        enter_btn = tk.Button(self.barcodeFrame, font=FONT, bg='#e8eb34', text='Enter',
                              command=lambda: [add_item_to_transactions_databases(
                                  item_database.getNameFromBarcode(int(self.barcodeEntry.get())),
                                  item_database.getSalePriceFromBarcode(int(self.barcodeEntry.get())),
                                  str(datetime.datetime.today()).split(' ')[0],
                                  item_database.getOPFromBarcode(int(self.barcodeEntry.get()))),
                                  barcodes.append(int(self.barcodeEntry.get())),
                                  erase_previous_entry([self.barcodeEntry]), show_transaction_table(self.tb_frame,
                                                                                                    self.tb_frame_1),
                                  click_on_barcode_entry()])

        self.barcodeEntry.bind('<Return>', lambda event: [enter_btn.invoke(), click_on_barcode_entry()])
        enter_btn.place(relx=0.85, rely=0.31, relheight=0.4, relwidth=0.1)

        self.return_img = tk.PhotoImage(file='return.png')
        return_btn = tk.Button(self, font=FONT, image=self.return_img, bg='#f0d807',
                               command=lambda: [return_window()])
        return_btn.place(relx=0.0, rely=0.4, relheight=0.1, relwidth=0.1)

        self.discount_img = tk.PhotoImage(file='discount.png')
        discount_btn = tk.Button(self, font=FONT, image=self.discount_img, bg='#0bdb70',
                                 command=lambda: [discount_window()])
        discount_btn.place(relx=0.0, rely=0.5, relheight=0.1, relwidth=0.1)

        self.misc_img = tk.PhotoImage(file='misc.png')
        misc_btn = tk.Button(self, font=FONT, image=self.misc_img, bg='#f53a18',
                             command=lambda: [misc_window(self.tb_frame, self.tb_frame_1)])
        misc_btn.place(relx=0.0, rely=0.6, relheight=0.1, relwidth=0.1)

        self.online_img = tk.PhotoImage(file='online_shop.png')
        online_btn = tk.Button(self, font=FONT, image=self.online_img, bg='#f405fc',
                               command=lambda: [online_transaction(self),
                                                erase_previous_entry([self.barcodeEntry])])
        online_btn.place(relx=0.0, rely=0.7, relheight=0.1, relwidth=0.1)

        offline_label(self)

        self.barcodeEntry.bind('r', lambda event: [return_btn.invoke()])

        self.barcodeEntry.bind('d', lambda event: [discount_btn.invoke()])

        self.barcodeEntry.bind('m', lambda event: [misc_btn.invoke()])

        self.barcodeEntry.bind('o', lambda event: [online_btn.invoke()])

        self.barcodeEntry.bind('<Delete>',
                               lambda event: [delete_pressed(self.tb_frame, self.tb_frame_1), click_on_barcode_entry()])

        # Add a Done/Save button
        done_btn = tk.Button(self, text='Done', bg='#eb3434', font=FONT,
                             command=lambda: [update_receipt_text(), controller.show_frame(MainPage),
                                              print_option(barcodes),
                                              barcodes.clear()])
        done_btn.place(relx=0.4, rely=0.9, relheight=0.05, relwidth=0.1)

        # Adding a back button
        back_btn = tk.Button(self, bg=BACK_BUTTON_COLOR, font=FONT, text='Back',
                             command=lambda: controller.show_frame(MainPage))
        back_btn.place(relx=0.5, rely=0.9, relheight=0.05, relwidth=0.1)

    def post_update(self):
        self.barcodeEntry.focus_force()


# AnalysisPage view
class AnalysisPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Background Label
        self.bgImg = tk.PhotoImage(file='background.png')
        bg_label = tk.Label(self, image=self.bgImg)
        bg_label.place(relheight=1, relwidth=1, anchor='nw')

        # show month rev analysis button
        show_month_rev_btn = tk.Button(self, fg='#fffafa', bg=BACKGROUND_FRAME_COLOR, font=FONT,
                                       text='Show Month by Month Rev.',
                                       command=lambda: show_monthly_analysis(self))
        show_month_rev_btn.place(relx=0.05, rely=0.1, relheight=0.1, relwidth=0.4)

        # show sales frequency analysis button
        show_sale_frequency_analysis_btn = tk.Button(self, fg='#fffafa', bg=BACKGROUND_FRAME_COLOR, font=FONT,
                                                     text='Show Top Selling Items',
                                                     command=lambda: show_sale_frequency_analysis(self))
        show_sale_frequency_analysis_btn.place(relx=0.55, rely=0.1, relheight=0.1, relwidth=0.4)

        # Add Back Button
        back_btn_frame = tk.Frame(self, bg=BACKGROUND_FRAME_COLOR)
        back_btn_frame.place(relx=0.4, rely=0.85, relheight=0.1, relwidth=0.2)
        back_btn = tk.Button(back_btn_frame, bg=BACK_BUTTON_COLOR, font=FONT, text='Back',
                             command=lambda: controller.show_frame(MainPage))
        back_btn.place(relx=0.25, rely=0.3, relheight=0.5, relwidth=0.5)


if __name__ == '__main__':
    app = InventoryApp()
    app.title("Inventory App")
    app.mainloop()
