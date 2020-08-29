# InventoryApp
TLDR; A Point of Sales System Application made using Python.
# WHY?
The primary reason I made this app is to allow small businesses to have an option to set up a FREE POS system on their laptop or computer. Professional POS software sell on the market for thousands of dollars, which can be a substantial cost for a small business owner. My goal in this project was to provide as many features that would be in a professional POS system while adding my own touches here and there. __Simply said, I wanted it to be simple to use, yet provide powerful features to the store owner/employee.__ 
# Real-life Test
The project idea was actually given by my dad who owns a liquor store himself. He was using an old-school POS system that was fast, yet simple and featureless. So, this summer I took on the task to create one myself and put it to test by letting my dad perform transactions and keep track of inventory while taking suggestions on more features that would be helpful throughout the way. 
# Features List
1) See, Add, Update Inventory 
2) Excel Sheet Tracking (both local and optionally, on google drive cloud)
3) Allows user to add different price for online selling (ex. for Uber Eats) 
4) Perform Transactions (using barcode scanner and even usb-printer for printing receipts)
5) Transactions UI allows the following windows: Return (to see how much you owe the customer when they give you a bill above their cost), Miscellaneous (to quickly add an item that you currently don't have in your inventory but know the price of), Discount (to add discount to a customer's total cost). Finally, there is a button to enter "Online/Offline" mode)
6) Analysis page that allows user to see top 10 selling items and also month-by-month revenue
7) NEW: See a live dashboard displaying your total inventory, sales, taxes, sale graphs, and much more! 
# Using the Application
- Open terminal
- Create a project directory: `mkdir whatever_name_you_want`
- Clone the repository: `git clone https://github.com/neesarg123/InventoryApp.git`
- Download required dependecies: `$ pip install -r requirements.txt`
- Open "Inputs.txt" file, enter the asked information (printer name, google sheet file name, google worksheet name).
- You can also add your inventory by clicking on "Inventory.xlsx" file in the directory and adding your store items. Alternatively, you can do this using the application, however, doing so in excel will likely be faster. 
- Run main.py: `$ python main.py` 
- __In a separate terminal window, open up the app directory using `cd the_name_of_the_project_directory`__ and then, type: `python dashboard.py`
- Click the link that pops up to see your live dashboard
## Alternative
- Go here: https://mega.nz/folder/CmhxCICY#9re-Dlwt03QYoFpdhWHJQg
- Download the "App" folder as a zip
- Extract the zip file
- Open "Inputs.txt" file, enter the asked information (printer name, google sheet file name, google worksheet name).
- Click on 'main.exe' to run the application
