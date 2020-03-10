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

# colors
BACKGROUND_FRAME_COLOR = '#42423f'
BUTTON_AND_LABEL_COLOR = '#adada6'
BACK_BUTTON_COLOR = '#d93027'
ENTRY_COLOR = '#d9d1d0'
# font
FONT = ('Courier', 15, 'bold')

# At the start of each run, two data frames need to get populated: inventory_df and all_transactions_df
inventory_data = {'Name': [names[0] for names in item_database.getNames()],
                  'Barcode': [barcodes[0] for barcodes in item_database.getBarcodes()],
                  'S.Price': [s_prices[0] for s_prices in item_database.getSPrices()],
                  'P.Price': [p_prices[0] for p_prices in item_database.getPPrices()],
                  'Quantity': [qtns[0] for qtns in item_database.getQtns()]}
inventory_df = pd.DataFrame(data=inventory_data)

all_transactions_data = {"Name": [names[0] for names in all_transactions_database.getNames()],
                         "S.Price": [s_prices[0] for s_prices in all_transactions_database.getSPrices()],
                         "Date": [dates[0] for dates in all_transactions_database.getDates()],
                         "P.Price": [p_prices[0] for p_prices in all_transactions_database.getPPrices()]}
all_transactions_df = pd.DataFrame(data=all_transactions_data)


# Misc. helper functions
def updated_all_transaction_data_frame():
    """returns updated all_transaction data frame"""
    all_transactions_data = {"Name": [names[0] for names in all_transactions_database.getNames()],
                             "S.Price": [s_prices[0] for s_prices in all_transactions_database.getSPrices()],
                             "Date": [dates[0] for dates in all_transactions_database.getDates()],
                             "P.Price": [p_prices[0] for p_prices in all_transactions_database.getPPrices()]}

    new_all_transactions_df = pd.DataFrame(data=all_transactions_data)
    return new_all_transactions_df


def updated_inventory_data_frame():
    """returns updated inventory data frame"""
    inventory_data = {'Name': [names[0] for names in item_database.getNames()],
                      'Barcode': [barcodes[0] for barcodes in item_database.getBarcodes()],
                      'S.Price': [s_prices[0] for s_prices in item_database.getSPrices()],
                      'P.Price': [p_prices[0] for p_prices in item_database.getPPrices()],
                      'Quantity': [qtns[0] for qtns in item_database.getQtns()]}
    new_inventory_df = pd.DataFrame(data=inventory_data)
    return new_inventory_df


def update_excel_files():
    """updates the excel files for both data frames"""
    updated_inventory_data_frame().to_excel('Inventory.xlsx', index=False)
    updated_all_transaction_data_frame().to_excel('Transactions.xlsx', index=False)


def erase_previous_entry(entries):
    """sets entry widget to blank"""
    for entry in entries:
        entry.delete(0, 'end')
        entry.focus_set()


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
                                    'Quantity': items[i][4]}

    table = TableCanvas(item_list_frame, data=data)
    table.show()


def show_transaction_table(frame, frame1):
    """displays the transactions table onto a tkinter table"""
    TableModel()
    transaction_items = transactions_database.getData()

    data = {}
    data1 = {}

    total_sale = Decimal(0.0)

    for i in range(len(transaction_items)):
        # setting precision length of decimal
        getcontext().prec = 5
        total_sale += Decimal(transaction_items[i][1])

    for i in range(len(transaction_items)):
        data['row' + str(i + 1)] = {'Name': transaction_items[i][0], 'S.Price': transaction_items[i][1],
                                    'Date': transaction_items[i][2]}

        data1['row1'] = {'Total ($)': str(total_sale)}

        table1 = TableCanvas(frame1, data=data1, takefocus=0)
        table = TableCanvas(frame, data=data, takefocus=0)

        table.show()
        table1.show()


def done_btn_pressed():
    """deletes the transactions database table, so it can be empty for the next transaction event"""
    transactions_database.deleteData()


def show_monthly_analysis(frame):
    """displays monthly revenue bar graph"""
    # Adding the revenue bar graph
    fig = Figure(figsize=(5, 5), dpi=80)
    subplot = fig.add_subplot(111)
    updated_at_df = pd.read_excel('Transactions.xlsx')
    updated_at_df['Revenue'] = updated_at_df['S.Price'] - updated_at_df['P.Price']
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
    subplot.set_ylabel('Revenue ($)')
    subplot.set_title('Revenue Per Month for Year 2020')
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
    subplot1.set_ylabel("Sale Frequency")

    # displaying the bar graph onto tkinter window
    canvas1 = FigureCanvasTkAgg(fig1, frame)
    canvas1.draw()
    canvas1.get_tk_widget().place(relx=0.55, rely=0.3, relheight=0.5, relwidth=0.4)


# Helper functions referenced in pages (to add/show/update items, transactions into databases, etc.)
def add_item_to_item_database(name, barcode, pp, sp, qtn, text):
    """takes in necessary parameters and adds item into the item_database table"""
    if (barcode,) in item_database.getBarcodes():
        text.set("Item is already in your inventory :)")  # sets the text of message label
    else:
        item_database.addData(name, barcode, pp, sp, qtn)
        text.set("Item was added :)")  # sets the text of message label


def add_item_to_transactions_databases(name, sp, date, pp):
    """takes in necessary parameters and adds item into transactions and all_transactions table"""
    transactions_database.addData(name, sp, date)
    all_transactions_database.addData(name, sp, date, pp)


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


def decrease_qtn(barcode):
    """takes in barcode and decrements quantity of that item by 1--used when committing transactions"""
    item_database.decreaseQuantityByOne(barcode)


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
        pages = (MainPage, InventoryPage, AddInventoryPage, SeeItemsPage, UpdatePage, UpdatingNamePage,
                 UpdatingPPPage, UpdatingSPPage, UpdatingQtnPage, TransactionPage, AnalysisPage)

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
        transaction_btn = tk.Button(frame, image=self.transaction_btn_image, text='Transaction Mode',
                                    bg=BUTTON_AND_LABEL_COLOR, command=lambda: controller.show_frame(TransactionPage),
                                    font=FONT)
        transaction_btn.place(relx=0.58, rely=0.05, relheight=0.9, relwidth=0.4)

        # Adding Show Monthly Revenue button
        analysis_frame = tk.Frame(self, bg=BACKGROUND_FRAME_COLOR)
        analysis_frame.place(relx=0.25, rely=0.7, relheight=0.15, relwidth=0.5)
        analysis_btn = tk.Button(analysis_frame, text='Show Analysis', bg=BUTTON_AND_LABEL_COLOR,
                                 font=FONT, command=lambda: [update_excel_files(), controller.show_frame(AnalysisPage)])
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
        barcode_entry.place(relx=0.45, rely=0.2, relheight=0.1, relwidth=0.3)
        barcode_entry_label.place(relx=0.25, rely=0.2, relheight=0.1, relwidth=0.2)
        # purchase price
        pp_entry = tk.Entry(frame, font=FONT, bg=ENTRY_COLOR)
        pp_entry_label = tk.Label(frame, bg=BUTTON_AND_LABEL_COLOR, text='P.Price', font=FONT,)
        pp_entry.place(relx=0.45, rely=0.35, relheight=0.1, relwidth=0.3)
        pp_entry_label.place(relx=0.25, rely=0.35, relheight=0.1, relwidth=0.2)
        # sale price
        sp_entry = tk.Entry(frame, font=FONT, bg=ENTRY_COLOR)
        sp_entry_label = tk.Label(frame, bg=BUTTON_AND_LABEL_COLOR, font=FONT, text='S.Price')
        sp_entry.place(relx=0.45, rely=0.5, relheight=0.1, relwidth=0.3)
        sp_entry_label.place(relx=0.25, rely=0.5, relheight=0.1, relwidth=0.2)
        # quantity
        qtn_entry = tk.Entry(frame, font=FONT, bg=ENTRY_COLOR)
        qtn_entry_label = tk.Label(frame, bg=BUTTON_AND_LABEL_COLOR, font=FONT, text='Quantity')
        qtn_entry.place(relx=0.45, rely=0.65, relheight=0.1, relwidth=0.3)
        qtn_entry_label.place(relx=0.25, rely=0.65, relheight=0.1, relwidth=0.2)

        # setting text of message (will appear when item is added)
        self.text = tk.StringVar()
        self.text.set("")
        # message label
        message_label = tk.Label(frame, bg=BACKGROUND_FRAME_COLOR, font=FONT, fg='#fffafa', textvariable=self.text)
        message_label.place(relx=0.1, rely=0.90, relheight=0.05, relwidth=0.8)

        # Add Item Button
        add_item_btn = tk.Button(frame, bg='#e8eb34', font=FONT, text='ADD', command=lambda: [
            add_item_to_item_database(name_entry.get(), int(barcode_entry.get()), pp_entry.get(),
                                      sp_entry.get(), int(qtn_entry.get()), self.text),
            erase_previous_entry([name_entry, barcode_entry, sp_entry, pp_entry, qtn_entry]), update_excel_files(),
            updated_all_transaction_data_frame(), updated_inventory_data_frame()])
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
        # new frame to see data
        update_option_frame = tk.Frame(self, bg=BACKGROUND_FRAME_COLOR)
        update_option_frame.place(relx=0.1, rely=0.5, relheight=0.1, relwidth=0.8)

        # adding the buttons
        update_name_btn = tk.Button(update_option_frame, bg=BUTTON_AND_LABEL_COLOR, font=FONT,
                                    text='Name',
                                    command=lambda: controller.show_frame(UpdatingNamePage))
        update_name_btn.place(relx=0.025, rely=0.25, relheight=0.5, relwidth=0.8 / 4)

        update_pp_btn = tk.Button(update_option_frame, bg=BUTTON_AND_LABEL_COLOR, font=FONT,
                                  text='P.Price',
                                  command=lambda: controller.show_frame(UpdatingPPPage))
        update_pp_btn.place(relx=(0.8 / 4) + 0.02 + 0.05, rely=0.25, relheight=0.5, relwidth=0.8 / 4)

        update_sp_btn = tk.Button(update_option_frame, bg=BUTTON_AND_LABEL_COLOR, font=FONT,
                                  text='S.Price',
                                  command=lambda: controller.show_frame(UpdatingSPPage))
        update_sp_btn.place(relx=(0.8 / 4) * 2 + 0.02 + 0.05 + 0.05, rely=0.25, relheight=0.5, relwidth=0.8 / 4)

        update_qtn_btn = tk.Button(update_option_frame, bg=BUTTON_AND_LABEL_COLOR, font=FONT,
                                   text='Quantity',
                                   command=lambda: controller.show_frame(UpdatingQtnPage))
        update_qtn_btn.place(relx=(0.8 / 4) * 3 + 0.02 + 0.05 + 0.05 + 0.05, rely=0.25, relheight=0.5, relwidth=0.8 / 4)

        # Add Back Button
        back_btn_frame = tk.Frame(self, bg=BACKGROUND_FRAME_COLOR)
        back_btn_frame.place(relx=0.4, rely=0.85, relheight=0.1, relwidth=0.2)
        back_btn = tk.Button(back_btn_frame, bg='#d93027', font=('Courier', 15, 'bold'), text='Back',
                             command=lambda: controller.show_frame(InventoryPage))
        back_btn.place(relx=0.25, rely=0.3, relheight=0.5, relwidth=0.5)

    def post_update(self):
        pass


# UpdatingNamePage view
class UpdatingNamePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Background Label
        self.bgImg = tk.PhotoImage(file='background.png')
        bg_label = tk.Label(self, image=self.bgImg)
        bg_label.place(relheight=1, relwidth=1, anchor='nw')

        # Adding a frame in the middle
        update_name_frame = tk.Frame(self, bg=BACKGROUND_FRAME_COLOR)
        update_name_frame.place(relx=0.2, rely=0.2, relheight=0.7, relwidth=0.6)

        # Adding entries and labels for barcode and new name
        # barcode
        self.enter_barcode_entry = tk.Entry(update_name_frame, bg=ENTRY_COLOR, font=FONT)
        self.enter_barcode_entry.focus()
        enter_barcode_entry_label = tk.Label(update_name_frame, bg=BUTTON_AND_LABEL_COLOR, font=FONT,
                                             text='Enter Barcode')
        enter_barcode_entry_label.place(relx=0.3, rely=0.1, relheight=0.1, relwidth=0.4)
        self.enter_barcode_entry.place(relx=0.3, rely=0.2, relheight=0.1, relwidth=0.4)
        # new name
        enter_name_entry = tk.Entry(update_name_frame, bg=ENTRY_COLOR, font=FONT)
        enter_name_entry_label = tk.Label(update_name_frame, bg=BUTTON_AND_LABEL_COLOR, font=FONT,
                                          text='Enter New Name')
        enter_name_entry_label.place(relx=0.3, rely=0.4, relheight=0.1, relwidth=0.4)
        enter_name_entry.place(relx=0.3, rely=0.5, relheight=0.1, relwidth=0.4)

        # setting text
        self.text = tk.StringVar()
        self.text.set("")
        # message label
        message_label = tk.Label(update_name_frame, bg=BACKGROUND_FRAME_COLOR, font=FONT, fg='#fffafa',
                                 textvariable=self.text)
        message_label.place(relx=0.1, rely=0.8, relheight=0.05, relwidth=0.8)

        # updating name button
        update_name_btn = tk.Button(update_name_frame, bg='#e8eb34', font=FONT, text='Update',
                                    command=lambda: [update_name(enter_name_entry.get(),
                                                                 int(self.enter_barcode_entry.get()), self.text),
                                                     erase_previous_entry([self.enter_barcode_entry,
                                                                           enter_name_entry])])
        update_name_btn.place(relx=0.35, rely=0.7, relheight=0.1, relwidth=0.3)

        # Back Button
        back_btn_frame = tk.Frame(self, bg='#42423f')
        back_btn_frame.place(relx=0.4, rely=0.85, relheight=0.1, relwidth=0.2)
        back_btn = tk.Button(back_btn_frame, bg='#d93027', font=('Courier', 15, 'bold'), text='Back',
                             command=lambda: controller.show_frame(UpdatePage))
        back_btn.place(relx=0.25, rely=0.3, relheight=0.5, relwidth=0.5)

    def post_update(self):
        self.enter_barcode_entry.focus()


# UpdatePPPage view
class UpdatingPPPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Background Label
        self.bgImg = tk.PhotoImage(file='background.png')
        bg_label = tk.Label(self, image=self.bgImg)
        bg_label.place(relheight=1, relwidth=1, anchor='nw')

        # Adding a frame in the middle
        update_pp_frame = tk.Frame(self, bg=BACKGROUND_FRAME_COLOR)
        update_pp_frame.place(relx=0.2, rely=0.2, relheight=0.7, relwidth=0.6)

        # Placing entries and labels for barcode and new pp
        # barcode
        self.enter_barcode_entry = tk.Entry(update_pp_frame, bg=ENTRY_COLOR, font=FONT)
        self.enter_barcode_entry.focus()
        enter_barcode_entry_label = tk.Label(update_pp_frame, bg=BUTTON_AND_LABEL_COLOR, font=FONT,
                                             text='Enter Barcode')
        enter_barcode_entry_label.place(relx=0.3, rely=0.1, relheight=0.1, relwidth=0.4)
        self.enter_barcode_entry.place(relx=0.3, rely=0.2, relheight=0.1, relwidth=0.4)
        # new pp
        enter_pp_entry = tk.Entry(update_pp_frame, bg=ENTRY_COLOR, font=FONT)
        enter_pp_entry_label = tk.Label(update_pp_frame, bg=BUTTON_AND_LABEL_COLOR, font=FONT, text='New P.Price')
        enter_pp_entry_label.place(relx=0.3, rely=0.4, relheight=0.1, relwidth=0.4)
        enter_pp_entry.place(relx=0.3, rely=0.5, relheight=0.1, relwidth=0.4)

        # setting text
        self.text = tk.StringVar()
        self.text.set("")
        # message label
        message_label = tk.Label(update_pp_frame, bg=BACKGROUND_FRAME_COLOR, font=FONT, fg='#fffafa',
                                 textvariable=self.text)
        message_label.place(relx=0.1, rely=0.8, relheight=0.05, relwidth=0.8)

        # update button to update the new pp for the item
        update_pp_btn = tk.Button(update_pp_frame, bg='#e8eb34', font=FONT, text='Update',
                                  command=lambda: [update_pp((enter_pp_entry.get()),
                                                             int(self.enter_barcode_entry.get()),
                                                             self.text), erase_previous_entry([self.enter_barcode_entry,
                                                                                               enter_pp_entry])])
        update_pp_btn.place(relx=0.35, rely=0.7, relheight=0.1, relwidth=0.3)

        # Add Back Button
        back_btn_frame = tk.Frame(self, bg=BACKGROUND_FRAME_COLOR)
        back_btn_frame.place(relx=0.4, rely=0.85, relheight=0.1, relwidth=0.2)
        back_btn = tk.Button(back_btn_frame, bg=BACK_BUTTON_COLOR, font=FONT, text='Back',
                             command=lambda: controller.show_frame(UpdatePage))
        back_btn.place(relx=0.25, rely=0.3, relheight=0.5, relwidth=0.5)

    def post_update(self):
        self.enter_barcode_entry.focus()


# UpdatingSPPage view
class UpdatingSPPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Background Label
        self.bgImg = tk.PhotoImage(file='background.png')
        bg_label = tk.Label(self, image=self.bgImg)
        bg_label.place(relheight=1, relwidth=1, anchor='nw')

        # Adding a frame in the middle
        update_sp_frame = tk.Frame(self, bg=BACKGROUND_FRAME_COLOR)
        update_sp_frame.place(relx=0.2, rely=0.2, relheight=0.7, relwidth=0.6)

        # Placing entries and labels for barcode and new sp
        # barcode
        self.enter_barcode_entry = tk.Entry(update_sp_frame, bg=ENTRY_COLOR, font=FONT)
        self.enter_barcode_entry.focus()
        enter_barcode_entry_label = tk.Label(update_sp_frame, bg=BUTTON_AND_LABEL_COLOR, font=FONT,
                                             text='Enter Barcode')
        enter_barcode_entry_label.place(relx=0.3, rely=0.1, relheight=0.1, relwidth=0.4)
        self.enter_barcode_entry.place(relx=0.3, rely=0.2, relheight=0.1, relwidth=0.4)
        # new sp
        enter_sp_entry = tk.Entry(update_sp_frame, bg=ENTRY_COLOR, font=FONT)
        enter_sp_entry_label = tk.Label(update_sp_frame, bg=BUTTON_AND_LABEL_COLOR, font=FONT,
                                        text='New S.Price')
        enter_sp_entry_label.place(relx=0.3, rely=0.4, relheight=0.1, relwidth=0.4)
        enter_sp_entry.place(relx=0.3, rely=0.5, relheight=0.1, relwidth=0.4)

        # setting text
        self.text = tk.StringVar()
        self.text.set("")
        # message label
        message_label = tk.Label(update_sp_frame, bg=BACKGROUND_FRAME_COLOR, font=FONT, fg='#fffafa',
                                 textvariable=self.text)
        message_label.place(relx=0.1, rely=0.8, relheight=0.05, relwidth=0.8)

        # Update button to change sp of item in item_database table
        update_sp_btn = tk.Button(update_sp_frame, bg='#e8eb34', font=FONT, text='Update',
                                  command=lambda: [update_sp(enter_sp_entry.get(),
                                                             int(self.enter_barcode_entry.get()), self.text),
                                                   erase_previous_entry([self.enter_barcode_entry, enter_sp_entry])])
        update_sp_btn.place(relx=0.35, rely=0.7, relheight=0.1, relwidth=0.3)

        # Add Back Button
        back_btn_frame = tk.Frame(self, bg=BACKGROUND_FRAME_COLOR)
        back_btn_frame.place(relx=0.4, rely=0.85, relheight=0.1, relwidth=0.2)
        back_btn = tk.Button(back_btn_frame, bg=BACK_BUTTON_COLOR, font=FONT, text='Back',
                             command=lambda: controller.show_frame(UpdatePage))
        back_btn.place(relx=0.25, rely=0.3, relheight=0.5, relwidth=0.5)

    def post_update(self):
        self.enter_barcode_entry.focus()


# UpdatingQtnPage view
class UpdatingQtnPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Background Label
        self.bgImg = tk.PhotoImage(file='background.png')
        bg_label = tk.Label(self, image=self.bgImg)
        bg_label.place(relheight=1, relwidth=1, anchor='nw')

        # Adding a frame in the middle
        update_qtn_frame = tk.Frame(self, bg=BACKGROUND_FRAME_COLOR)
        update_qtn_frame.place(relx=0.2, rely=0.2, relheight=0.7, relwidth=0.6)

        # Placing entries and labels for barcode and new qtn
        # barcode
        self.enter_barcode_entry = tk.Entry(update_qtn_frame, bg=ENTRY_COLOR, font=FONT)
        self.enter_barcode_entry.focus()
        enter_barcode_entry_label = tk.Label(update_qtn_frame, bg=BUTTON_AND_LABEL_COLOR, font=FONT,
                                             text='Enter Barcode')
        enter_barcode_entry_label.place(relx=0.3, rely=0.1, relheight=0.1, relwidth=0.4)
        self.enter_barcode_entry.place(relx=0.3, rely=0.2, relheight=0.1, relwidth=0.4)
        # new qtn
        enter_qtn_entry = tk.Entry(update_qtn_frame, bg=ENTRY_COLOR, font=FONT)
        enter_qtn_entry_label = tk.Label(update_qtn_frame, bg=BUTTON_AND_LABEL_COLOR, font=FONT,
                                         text='New Quantity')
        enter_qtn_entry_label.place(relx=0.3, rely=0.4, relheight=0.1, relwidth=0.4)
        enter_qtn_entry.place(relx=0.3, rely=0.5, relheight=0.1, relwidth=0.4)

        # setting text
        self.text = tk.StringVar()
        self.text.set("")
        # message label
        message_label = tk.Label(update_qtn_frame, bg=BACKGROUND_FRAME_COLOR, font=FONT, fg='#fffafa',
                                 textvariable=self.text)
        message_label.place(relx=0.1, rely=0.8, relheight=0.05, relwidth=0.8)

        # update button
        update_qtn_btn = tk.Button(update_qtn_frame, bg='#e8eb34', font=FONT, text='Update',
                                   command=lambda: [update_qtn(enter_qtn_entry.get(),
                                                               int(self.enter_barcode_entry.get()), self.text),
                                                    erase_previous_entry([self.enter_barcode_entry, enter_qtn_entry])])
        update_qtn_btn.place(relx=0.35, rely=0.7, relheight=0.1, relwidth=0.3)

        # Add Back Button
        back_btn_frame = tk.Frame(self, bg=BACKGROUND_FRAME_COLOR)
        back_btn_frame.place(relx=0.4, rely=0.85, relheight=0.1, relwidth=0.2)
        back_btn = tk.Button(back_btn_frame, bg=BACK_BUTTON_COLOR, font=FONT, text='Back',
                             command=lambda: controller.show_frame(UpdatePage))
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
        tb_frame = tk.Frame(self, bg=BACKGROUND_FRAME_COLOR)
        tb_frame.place(relx=0.1, rely=0.3, relheight=0.6, relwidth=0.6)
        # Table Frame (to view total bill)
        tb_frame_1 = tk.Frame(self, bg=BACKGROUND_FRAME_COLOR)
        tb_frame_1.place(relx=0.7, rely=0.3, relheight=0.6, relwidth=0.2)

        # Adding an Enter button
        enter_btn = tk.Button(self.barcodeFrame, font=FONT, bg='#e8eb34', text='Enter',
                              command=lambda: [add_item_to_transactions_databases(
                                  item_database.getNameFromBarcode(int(self.barcodeEntry.get())),
                                  item_database.getSalePriceFromBarcode(int(self.barcodeEntry.get())),
                                  str(datetime.datetime.today()).split(' ')[0],
                                  item_database.getPPFromBarcode(int(self.barcodeEntry.get()))),
                                  decrease_qtn(self.barcodeEntry.get()),
                                  erase_previous_entry([self.barcodeEntry]), show_transaction_table(tb_frame,
                                                                                                    tb_frame_1)])

        self.barcodeEntry.bind('<Return>', lambda event: [enter_btn.invoke()])
        enter_btn.place(relx=0.85, rely=0.31, relheight=0.4, relwidth=0.1)

        # Add a Done/Save button
        done_btn = tk.Button(self, text='Done', bg='#eb3434', font=('Courier', 15, 'bold'),
                             command=lambda: [done_btn_pressed(), controller.show_frame(MainPage),
                                              update_excel_files(), updated_inventory_data_frame(),
                                              updated_all_transaction_data_frame()])
        done_btn.place(relx=0.45, rely=0.9, relheight=0.05, relwidth=0.1)

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
                                                     text='Show Month by Month Rev.',
                                                     command=lambda: show_sale_frequency_analysis(self))
        show_sale_frequency_analysis_btn.place(relx=0.55, rely=0.1, relheight=0.1, relwidth=0.4)

        # Add Back Button
        back_btn_frame = tk.Frame(self, bg=BACKGROUND_FRAME_COLOR)
        back_btn_frame.place(relx=0.4, rely=0.85, relheight=0.1, relwidth=0.2)
        back_btn = tk.Button(back_btn_frame, bg=BACK_BUTTON_COLOR, font=FONT, text='Back',
                             command=lambda: controller.show_frame(MainPage))
        back_btn.place(relx=0.25, rely=0.3, relheight=0.5, relwidth=0.5)


if __name__ == '__main__':
    # adding a revenue column (sp - pp) to all_transactions data frame
    all_transactions_df['Revenue'] = all_transactions_df['S.Price'] - all_transactions_df['P.Price']
    app = InventoryApp()
    app.title("Neesarg's Inventory App")
    app.mainloop()
