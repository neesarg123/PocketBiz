import tkinter as tk
from tkinter import font
import item_database
import transactions_database
import all_transactions_database
from tkintertable import TableCanvas, TableModel
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import time
import openpyxl as op

names = []
barcodes = []
sprices = []
pprices = []
quantities = []

names_at = []
sprices_at = []
date_at = []
pprices_at = []

for item in item_database.getData():
    names.append(item[0])
    barcodes.append(item[1])
    sprices.append(item[2])
    pprices.append(item[3])
    quantities.append(item[4])

for item in all_transactions_database.getData():
    names_at.append(item[0])
    sprices_at.append(item[1])
    date_at.append(item[2])
    pprices_at.append(item[3])

data = {"Name": names, "Barcode": barcodes, "S.Price": sprices, "P.Price": pprices, "Quantity": quantities}
data1 = {"Name": names_at, "S.Price": sprices_at, "Date": date_at, "P.Price": pprices_at}

inventoryDf = pd.DataFrame(data=data)
df = pd.DataFrame(data=data1)


def update_dframes():
    names.clear()
    barcodes.clear()
    sprices.clear()
    pprices.clear()
    quantities.clear()

    names_at.clear()
    sprices_at.clear()
    date_at.clear()
    pprices_at.clear()

    for item in item_database.getData():
        names.append(item[0])
        barcodes.append(item[1])
        sprices.append(item[2])
        pprices.append(item[3])
        quantities.append(item[4])

    for item in all_transactions_database.getData():
        names_at.append(item[0])
        sprices_at.append(item[1])
        date_at.append(item[2])
        pprices_at.append(item[3])

    data = {"Name": names, "Barcode": barcodes, "S.Price": sprices, "P.Price": pprices, "Quantity": quantities}
    data1 = {"Name": names_at, "S.Price": sprices_at, "Date": date_at, "P.Price": pprices_at}

    new_inventory_df = pd.DataFrame(data=data)
    new_at_df = pd.DataFrame(data=data1)
    inventoryDf = new_inventory_df
    df = new_at_df

    df.to_excel('Transactions.xlsx', index=False)
    inventoryDf.to_excel('Inventory.xlsx', sheet_name='Inventory', index=False)


def add_item(name, barcode, pp, sp, qtn):
    item_database.addData(name, barcode, pp, sp, qtn)


def add_item_to_transactions(name, sp, date, pp):
    transactions_database.addData(name, sp, date)
    all_transactions_database.addData(name, sp, date, pp)


def update_name(newName, barcode):
    item_database.updateName(newName, barcode)


def update_pp(newPP, barcode):
    item_database.updatePurchasePrice(newPP, barcode)


def update_sp(newSP, barcode):
    item_database.updateSalePrice(newSP, barcode)


def update_qnt(newQtn, barcode):
    item_database.updateQuantity(newQtn, barcode)


def decreaseQtn(barcode):
    item_database.decreaseQuantityByOne(barcode)


def done_btn_pressed():
    transactions_database.deleteData()


def show_transaction_table(frame, frame1):
    model = TableModel()
    transactionItems = transactions_database.getData()

    data = {}
    data1 = {}

    totalSale = 0.0

    for i in range(len(transactionItems)):
        totalSale += float(transactionItems[i][1])

    for i in range(len(transactionItems)):
        data['row' + str(i + 1)] = {'Name': transactionItems[i][0], 'S.Price': transactionItems[i][1],
                                    'Date': transactionItems[i][2]}

        data1['row1'] = {'Total ($)': totalSale}

        table1 = TableCanvas(frame1, data=data1, takefocus=0)
        table = TableCanvas(frame, data=data, takefocus=0)

        table.show()
        table1.show()


def erase_previous_entry(Entry):
    Entry.delete(0, 'end')
    Entry.focus_set()


def showAnalysis():
    # Analysis
    df['Month'] = df['Date'].str[5:7]
    df['Month'] = df['Month'].astype('int32')

    monthlyRevs = df.groupby('Month').sum()
    months = [x for x in df['Month']]
    nonRepMonths = []
    for month in months:
        if month not in nonRepMonths:
            nonRepMonths.append(month)
    plt.xticks(nonRepMonths)
    plt.bar(nonRepMonths, monthlyRevs['Revenue'], color="#eb6e34")
    plt.title("Revenue Per Month for 2020")
    plt.xlabel("Month Number")
    plt.ylabel("Revenue ($)")
    plt.show()


class inventoryApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)
        container.pack(fill='both', expand=True)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        self.frames = {}

        for F in (MainPage, InventoryPage, AddInventoryPage, seeItemsPage, updatePage, updatingNamePage,
                  updatingPPPage, updatingSPPage, updatingQtnPage, transactionPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame(MainPage)

    def postupdate(self):
        pass

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()

        try:
            frame.postupdate()
        except AttributeError:
            pass


class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Canvas
        canvas = tk.Canvas(self, height=700, width=800)
        canvas.pack()

        # Background Label
        self.bgImg = tk.PhotoImage(file='background.png')
        bgLabel = tk.Label(self, image=self.bgImg)
        bgLabel.place(relheight=1, relwidth=1, anchor='nw')

        # Adding Buttons
        # Adding a frame in the middle
        frame = tk.Frame(self, bg='#eb4c34')
        frame.place(relx=0.125, rely=0.2, relheight=0.5, relwidth=0.75)
        # Adding inventory button
        self.inventory_btn_image = tk.PhotoImage(file='supplier.png')
        inventory_btn = tk.Button(frame, padx=24, image=self.inventory_btn_image,
                                  text="Access/Update" + "\n" + "Inventory", bg='#e8eb34', font=('Courier', 15, 'bold'),
                                  command=lambda: controller.show_frame(InventoryPage))
        inventory_btn.place(relx=0.02, rely=0.05, relheight=0.9, relwidth=0.4)
        # Adding transaction button
        self.transaction_btn_image = tk.PhotoImage(file='card-machine.png')
        transaction_btn = tk.Button(frame, image=self.transaction_btn_image, text='Transaction Mode', bg='#e8eb34',
                                    command=lambda: controller.show_frame(transactionPage),
                                    font=('Courier', 15, 'bold'))
        transaction_btn.place(relx=0.58, rely=0.05, relheight=0.9, relwidth=0.4)

        # Adding Show Monthly Revenue button
        frame1 = tk.Frame(self, bg='#eb4c34')
        frame1.place(relx=0.25, rely=0.7, relheight=0.15, relwidth=0.5)
        monthRevBtn = tk.Button(frame1, text='Show Analysis', bg='#34a1eb', font=('Courier', 14, 'bold'),
                                command=lambda: showAnalysis())
        monthRevBtn.place(relx=0.25, rely=0.2, relheight=0.5, relwidth=0.5)

    def postupdate(self):
        print("Main page was shown")
        pass


class InventoryPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Background Label
        self.bgImg = tk.PhotoImage(file='background.png')
        bgLabel = tk.Label(self, image=self.bgImg)
        bgLabel.place(relheight=1, relwidth=1, anchor='nw')

        # frame on top for all the buttons
        top_frame = tk.Frame(self, bg='#b53680')
        top_frame.place(relx=0.1, rely=0.5, relheight=0.1, relwidth=0.8)

        # adding 'see' button
        see_btn = tk.Button(top_frame, bg='#e8eb34', text='SEE', font=('Courier', 15, 'bold'),
                            command=lambda: controller.show_frame(seeItemsPage))
        see_btn.place(relx=0.02, rely=0.25, relheight=0.5, relwidth=0.8 / 3)

        # adding 'add' button
        add_btn = tk.Button(top_frame, bg='#e8eb34', text='ADD', font=('Courier', 15, 'bold'),
                            command=lambda: controller.show_frame(AddInventoryPage))
        add_btn.place(relx=0.8 / 3 + 0.1, rely=0.25, relheight=0.5, relwidth=0.8 / 3)

        # adding 'update' button
        update_btn = tk.Button(top_frame, bg='#e8eb34', text='UPDATE', font=('Courier', 15, 'bold'),
                               command=lambda: controller.show_frame(updatePage))
        update_btn.place(relx=(0.8 / 3) * 2 + 0.175, rely=0.25, relheight=0.5, relwidth=0.8 / 3)

        # Adding a back button
        backBtnFrame = tk.Frame(self, bg='#b53680')
        backBtnFrame.place(relx=0.4, rely=0.6, relheight=0.1, relwidth=0.2)
        backBtn = tk.Button(backBtnFrame, font=('Courier', 15, 'bold'), text='Back',
                            command=lambda: controller.show_frame(MainPage))
        backBtn.place(relx=0.25, rely=0.3, relheight=0.5, relwidth=0.5)

    def postupdate(self):
        pass


class AddInventoryPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Background Label
        self.bgImg = tk.PhotoImage(file='background.png')
        bgLabel = tk.Label(self, image=self.bgImg)
        bgLabel.place(relheight=1, relwidth=1, anchor='nw')

        # Adding Item Frame
        frame = tk.Frame(self, bg='#6f36b5')
        frame.place(relx=0.1, rely=0.1, relheight=0.8, relwidth=0.8)

        # Adding Entries
        # name entry
        name_entry = tk.Entry(frame)
        name_entry.focus()
        name_entry_label = tk.Label(frame, text='Enter Name')
        name_entry.place(relx=0.12, rely=0.05, relheight=0.1, relwidth=0.4)
        name_entry_label.place(relx=0.02, rely=0.05, relheight=0.1, relwidth=0.1)
        # barcode entry
        barcode_entry = tk.Entry(frame)
        barcode_entry_label = tk.Label(frame, text='Barcode')
        barcode_entry.place(relx=0.12, rely=0.2, relheight=0.1, relwidth=0.4)
        barcode_entry_label.place(relx=0.02, rely=0.2, relheight=0.1, relwidth=0.1)
        # purchase price
        pp_entry = tk.Entry(frame)
        pp_entry_label = tk.Label(frame, text='P.Price')
        pp_entry.place(relx=0.12, rely=0.35, relheight=0.1, relwidth=0.4)
        pp_entry_label.place(relx=0.02, rely=0.35, relheight=0.1, relwidth=0.1)
        # sale price
        sp_entry = tk.Entry(frame)
        sp_entry_label = tk.Label(frame, text='S.Price')
        sp_entry.place(relx=0.12, rely=0.5, relheight=0.1, relwidth=0.4)
        sp_entry_label.place(relx=0.02, rely=0.5, relheight=0.1, relwidth=0.1)
        # quantity
        qtn_entry = tk.Entry(frame)
        qtn_entry_label = tk.Label(frame, text='Quantity')
        qtn_entry.place(relx=0.12, rely=0.65, relheight=0.1, relwidth=0.4)
        qtn_entry_label.place(relx=0.02, rely=0.65, relheight=0.1, relwidth=0.1)

        # Add Item Button
        add_item_btn = tk.Button(frame, bg='#e8eb34', font=('Courier', 15, 'bold'), text='ADD', command=lambda: [
            add_item(name_entry.get(), int(barcode_entry.get()), float(pp_entry.get()), float(sp_entry.get()),
                     int(qtn_entry.get())), erase_previous_entry(name_entry),
            erase_previous_entry(barcode_entry), update_dframes(), erase_previous_entry(sp_entry),
            erase_previous_entry(pp_entry), erase_previous_entry(qtn_entry)])
        add_item_btn.place(relx=0.02, rely=0.8, relheight=0.1, relwidth=0.1)

        # Add Back Button
        back_btn = tk.Button(frame, text='Back', font=('Courier', 15, 'bold'),
                             command=lambda: controller.show_frame(InventoryPage))
        back_btn.place(relx=0.22, rely=0.8, relheight=0.1, relwidth=0.1)

    def postupdate(self):
        pass


class seeItemsPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Background Label
        self.bgImg = tk.PhotoImage(file='background.png')
        bgLabel = tk.Label(self, image=self.bgImg)
        bgLabel.place(relheight=1, relwidth=1, anchor='nw')

        # new frame to see data
        self.itemsListFrame = tk.Frame(self, bg='#b536aa')
        self.itemsListFrame.place(relx=0.15, rely=0.2, relheight=0.6, relwidth=0.7)

        model = TableModel()
        items = item_database.getData()
        print(len(items))
        data = {}

        for i in range(len(items)):
            data['row' + str(i + 1)] = {'Name': items[i][0], 'Barcode': items[i][1],
                                        'P.Price': items[i][2], 'S.Price': items[i][3],
                                        'Quantity': items[i][4]}

        table = TableCanvas(self.itemsListFrame, data=data)
        table.show()

        # Add a new frame for back button
        frame = tk.Frame(self, bg='#b536aa')
        frame.place(relx=0.15, rely=0.8, relheight=0.1, relwidth=0.7)

        # Add Back Button
        back_btn = tk.Button(frame, text='Back', font=('Courier', 15, 'bold'),
                             command=lambda: controller.show_frame(InventoryPage))
        back_btn.place(relx=0.35, rely=0.3, relheight=0.3, relwidth=0.3)

    def postupdate(self):
        items = item_database.getData()
        print(len(items))
        data = {}

        for i in range(len(items)):
            data['row' + str(i + 1)] = {'Name': items[i][0], 'Barcode': items[i][1],
                                        'P.Price': items[i][2], 'S.Price': items[i][3],
                                        'Quantity': items[i][4]}

        table = TableCanvas(self.itemsListFrame, data=data)
        table.show()


class updatePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Background Label
        self.bgImg = tk.PhotoImage(file='background.png')
        bgLabel = tk.Label(self, image=self.bgImg)
        bgLabel.place(relheight=1, relwidth=1, anchor='nw')
        # new frame to see data
        updateOptionFrame = tk.Frame(self, bg='#b536aa')
        updateOptionFrame.place(relx=0.2, rely=0.2, relheight=0.6, relwidth=0.6)

        # adding the buttons
        update_name_btn = tk.Button(updateOptionFrame, bg='#e8eb34', font=('Courier', 15, 'bold'),
                                    text='Update' + '\n' + 'Name',
                                    command=lambda: controller.show_frame(updatingNamePage))
        update_name_btn.place(relx=0.01, rely=0.01, relheight=0.3, relwidth=0.3)

        update_pp_btn = tk.Button(updateOptionFrame, bg='#e8eb34', font=('Courier', 15, 'bold'),
                                  text='Update' + '\n' + 'P.Price',
                                  command=lambda: controller.show_frame(updatingPPPage))
        update_pp_btn.place(relx=0.69, rely=0.01, relheight=0.3, relwidth=0.3)

        update_sp_btn = tk.Button(updateOptionFrame, bg='#e8eb34', font=('Courier', 15, 'bold'),
                                  text='Update' + '\n' + 'S.Price',
                                  command=lambda: controller.show_frame(updatingSPPage))
        update_sp_btn.place(relx=0.01, rely=0.69, relheight=0.3, relwidth=0.3)

        update_qtn_btn = tk.Button(updateOptionFrame, bg='#e8eb34', font=('Courier', 15, 'bold'),
                                   text='Update' + '\n' + 'Quantity',
                                   command=lambda: controller.show_frame(updatingQtnPage))
        update_qtn_btn.place(relx=0.69, rely=0.69, relheight=0.3, relwidth=0.3)

        # Add Back Button
        back_btn = tk.Button(updateOptionFrame, text='Back', font=('Courier', 15, 'bold'),
                             command=lambda: controller.show_frame(InventoryPage))
        back_btn.place(relx=0.34, rely=0.34, relheight=0.3, relwidth=0.3)

    def postupdate(self):
        pass


class updatingNamePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Background Label
        self.bgImg = tk.PhotoImage(file='background.png')
        bgLabel = tk.Label(self, image=self.bgImg)
        bgLabel.place(relheight=1, relwidth=1, anchor='nw')

        updateNameFrame = tk.Frame(self, bg='#b536aa')
        updateNameFrame.place(relx=0.2, rely=0.2, relheight=0.7, relwidth=0.6)

        self.enterBarcodeEntry = tk.Entry(updateNameFrame)
        enterBarcodeEntryLabel = tk.Label(updateNameFrame, text='Enter Barcode')
        enterBarcodeEntryLabel.place(relx=0.4, rely=0.1, relheight=0.1, relwidth=0.2)
        self.enterBarcodeEntry.place(relx=0.35, rely=0.22, relheight=0.1, relwidth=0.3)

        enterNameEntry = tk.Entry(updateNameFrame)
        enterNameEntryLabel = tk.Label(updateNameFrame, text='Enter New Name')
        enterNameEntryLabel.place(relx=0.4, rely=0.4, relheight=0.1, relwidth=0.2)
        enterNameEntry.place(relx=0.35, rely=0.52, relheight=0.1, relwidth=0.3)

        updateNameBtn = tk.Button(updateNameFrame, bg='#e8eb34', font=('Courier', 15, 'bold'), text='Update',
                                  command=lambda: update_name(enterNameEntry.get(), int(self.enterBarcodeEntry.get())))
        updateNameBtn.place(relx=0.35, rely=0.7, relheight=0.1, relwidth=0.3)

        # Add a new Frame for back button
        frame = tk.Frame(self, bg='red')
        frame.place(relx=0.2, rely=0.8, relheight=0.1, relwidth=0.6)

        # Add Back Button
        back_btn = tk.Button(frame, text='Back', font=('Courier', 15, 'bold'),
                             command=lambda: controller.show_frame(updatePage))
        back_btn.place(relx=0.25, rely=0.25, relheight=0.5, relwidth=0.5)

    def postupdate(self):
        self.enterBarcodeEntry.focus()


class updatingPPPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Background Label
        self.bgImg = tk.PhotoImage(file='background.png')
        bgLabel = tk.Label(self, image=self.bgImg)
        bgLabel.place(relheight=1, relwidth=1, anchor='nw')

        updatePPFrame = tk.Frame(self, bg='#b536aa')
        updatePPFrame.place(relx=0.2, rely=0.2, relheight=0.7, relwidth=0.6)

        enterBarcodeEntry = tk.Entry(updatePPFrame)
        enterBarcodeEntry.focus()
        enterBarcodeEntry.place(relx=0.35, rely=0.22, relheight=0.1, relwidth=0.3)
        enterBarcodeEntryLabel = tk.Label(updatePPFrame, text='Enter Barcode')
        enterBarcodeEntryLabel.place(relx=0.4, rely=0.1, relheight=0.1, relwidth=0.2)

        enterPPEntry = tk.Entry(updatePPFrame)
        enterPPEntryLabel = tk.Label(updatePPFrame, text='Enter New P.Price')
        enterPPEntryLabel.place(relx=0.4, rely=0.4, relheight=0.1, relwidth=0.2)
        enterPPEntry.place(relx=0.35, rely=0.52, relheight=0.1, relwidth=0.3)

        updatePPBtn = tk.Button(updatePPFrame, bg='#e8eb34', font=('Courier', 15, 'bold'), text='Update',
                                command=lambda: update_pp((enterPPEntry.get()), int(enterBarcodeEntry.get())))
        updatePPBtn.place(relx=0.35, rely=0.7, relheight=0.1, relwidth=0.3)

        # Add a new Frame for back button
        frame = tk.Frame(self, bg='red')
        frame.place(relx=0.2, rely=0.8, relheight=0.1, relwidth=0.6)

        # Add Back Button
        back_btn = tk.Button(frame, text='Back', font=('Courier', 15, 'bold'),
                             command=lambda: controller.show_frame(updatePage))
        back_btn.place(relx=0.25, rely=0.25, relheight=0.5, relwidth=0.5)


class updatingSPPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Background Label
        self.bgImg = tk.PhotoImage(file='background.png')
        bgLabel = tk.Label(self, image=self.bgImg)
        bgLabel.place(relheight=1, relwidth=1, anchor='nw')

        updateSPFrame = tk.Frame(self, bg='#b536aa')
        updateSPFrame.place(relx=0.2, rely=0.2, relheight=0.7, relwidth=0.6)

        enterBarcodeEntry = tk.Entry(updateSPFrame)
        enterBarcodeEntryLabel = tk.Label(updateSPFrame, text='Enter Barcode')
        enterBarcodeEntryLabel.place(relx=0.4, rely=0.1, relheight=0.1, relwidth=0.2)
        enterBarcodeEntry.place(relx=0.35, rely=0.22, relheight=0.1, relwidth=0.3)

        enterSPEntry = tk.Entry(updateSPFrame)
        enterSPEntryLabel = tk.Label(updateSPFrame, text='Enter New S.Price')
        enterSPEntryLabel.place(relx=0.4, rely=0.4, relheight=0.1, relwidth=0.2)
        enterSPEntry.place(relx=0.35, rely=0.52, relheight=0.1, relwidth=0.3)

        updateSPBtn = tk.Button(updateSPFrame, bg='#e8eb34', font=('Courier', 15, 'bold'), text='Update',
                                command=lambda: update_sp(float(enterSPEntry.get()), int(enterBarcodeEntry.get())))
        updateSPBtn.place(relx=0.35, rely=0.7, relheight=0.1, relwidth=0.3)

        # Add a new Frame for back button
        frame = tk.Frame(self, bg='red')
        frame.place(relx=0.2, rely=0.8, relheight=0.1, relwidth=0.6)

        # Add Back Button
        back_btn = tk.Button(frame, text='Back', font=('Courier', 15, 'bold'),
                             command=lambda: controller.show_frame(updatePage))
        back_btn.place(relx=0.25, rely=0.25, relheight=0.5, relwidth=0.5)


class updatingQtnPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Background Label
        self.bgImg = tk.PhotoImage(file='background.png')
        bgLabel = tk.Label(self, image=self.bgImg)
        bgLabel.place(relheight=1, relwidth=1, anchor='nw')

        updateQtnFrame = tk.Frame(self, bg='#b536aa')
        updateQtnFrame.place(relx=0.2, rely=0.2, relheight=0.7, relwidth=0.6)

        enterBarcodeEntry = tk.Entry(updateQtnFrame)
        enterBarcodeEntryLabel = tk.Label(updateQtnFrame, text='Enter Barcode')
        enterBarcodeEntryLabel.place(relx=0.4, rely=0.1, relheight=0.1, relwidth=0.2)
        enterBarcodeEntry.place(relx=0.35, rely=0.22, relheight=0.1, relwidth=0.3)

        enterQtnEntry = tk.Entry(updateQtnFrame)
        enterQtnEntryLabel = tk.Label(updateQtnFrame, text='Enter New Quantity')
        enterQtnEntryLabel.place(relx=0.4, rely=0.4, relheight=0.1, relwidth=0.2)
        enterQtnEntry.place(relx=0.35, rely=0.52, relheight=0.1, relwidth=0.3)

        updateQtnBtn = tk.Button(updateQtnFrame, bg='#e8eb34', font=('Courier', 15, 'bold'), text='Update',
                                 command=lambda: update_qnt(float(enterQtnEntry.get()), int(enterBarcodeEntry.get())))
        updateQtnBtn.place(relx=0.35, rely=0.7, relheight=0.1, relwidth=0.3)

        # Add a new Frame for back button
        frame = tk.Frame(self, bg='red')
        frame.place(relx=0.2, rely=0.8, relheight=0.1, relwidth=0.6)

        # Add Back Button
        back_btn = tk.Button(frame, text='Back', font=('Courier', 15, 'bold'),
                             command=lambda: controller.show_frame(updatePage))
        back_btn.place(relx=0.25, rely=0.25, relheight=0.5, relwidth=0.5)


class transactionPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        transactions_database.deleteData()

        # Background Label
        self.bgImg = tk.PhotoImage(file='background.png')
        bgLabel = tk.Label(self, image=self.bgImg)
        bgLabel.place(relheight=1, relwidth=1, anchor='nw')

        # Adding a frame for the barcode entry
        self.barcodeFrame = tk.Frame(self, bg='#36b5a6')
        self.barcodeFrame.place(relx=0.1, rely=0.1, relheight=0.15, relwidth=0.8)

        # Scan Barcode Label
        scanLabel = tk.Label(self.barcodeFrame, text='Scan Barcode', bg='#36b5a6')
        scanLabel.place(relx=0.15, rely=0.1, relheight=0.14, relwidth=0.7)

        # Barcode Entry
        self.barcodeEntry = tk.Entry(self.barcodeFrame)
        print('barcodeEntry was made')
        self.barcodeEntry.place(relx=0.15, rely=0.3, relheight=0.4, relwidth=0.7)

        # Table Frame
        tbFrame = tk.Frame(self, bg='#36b5a6')
        tbFrame.place(relx=0.1, rely=0.3, relheight=0.6, relwidth=0.6)

        tbFram1 = tk.Frame(self, bg='#36b5a6')
        tbFram1.place(relx=0.7, rely=0.3, relheight=0.6, relwidth=0.2)

        # Add a Enter button
        enter_btn = tk.Button(self.barcodeFrame, font=('Courier', 15, 'bold'), bg='#e8eb34', text='Enter',
                              command=lambda: [add_item_to_transactions(
                                  item_database.getNameFromBarcode(int(self.barcodeEntry.get())),
                                  item_database.getSalePriceFromBarcode(int(self.barcodeEntry.get())),
                                  str(datetime.datetime.today()).split(' ')[0],
                                  item_database.getPPFromBarcode(int(self.barcodeEntry.get()))),
                                               erase_previous_entry(self.barcodeEntry),
                                               show_transaction_table(tbFrame, tbFram1)])

        self.barcodeEntry.bind('<Return>', lambda event: [enter_btn.invoke()])
        enter_btn.place(relx=0.85, rely=0.31, relheight=0.4, relwidth=0.1)

        # Add a Done/Save button
        done_btn = tk.Button(self, text='Done', bg='#eb3434', font=('Courier', 15, 'bold'),
                             command=lambda: [done_btn_pressed(), controller.show_frame(MainPage), update_dframes()])
        done_btn.place(relx=0.45, rely=0.9, relheight=0.05, relwidth=0.1)

    def postupdate(self):
        self.barcodeEntry.focus_force()
        print('transaction page was shown')


def main():
    df['Revenue'] = df['S.Price'] - df['P.Price']

    app = inventoryApp()
    app.title("Neesarg's Inventory App")
    app.mainloop()


main()
