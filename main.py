import os
import certifi
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from ShoeventoryAPI import get_shoeventory, login_auth
from POSApi import create_transaction
from excel_data_entry import add_shoe_to_excel, create_excel_file

os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()


# Sample shoe data (replace this with your actual data)


#shoe_data = [
#    {"ShoeID": 1, "Name": "Pandas", "Brand": "Nike", "Size": 9, "Color": "Black", "Quantity": 5, "Price": 100},
#    {"ShoeID": 2, "Name": "350v2", "Brand": "Adidas", "Size": 10, "Color": "White", "Quantity": 3, "Price": 200},
#    # Add more shoe data here as needed
#]
inventory_data = None  # Replace '1' with the merchant ID
shoe_data = None  # Access the list of shoes from the API response
cart = []
user_id = None
user = None
password = None
token = None
collection = None


# Function to validate the login credentials
def login():
    global user, password, token, shoe_data, inventory_data, user_id
    user = username_entry.get()
    password = password_entry.get()
    data = login_auth(user, password)
    token = data['token']
    user_id = data['merchantId']
    if token is not None:
        inventory_data = get_shoeventory(user_id, token)
        login_window.destroy()
        open_main_window()
        create_excel_file()
    else:
        messagebox.showinfo("Login Failed", "Invalid username or password.")
        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)


def logout():
    global user, password, token, shoe_data, inventory_data, user_id
    user = None
    password = None
    token = None
    shoe_data = None
    inventory_data = None
    user_id = None
    close_main_window()
    login_window = tk.Tk()
    login_window.title("Login")
    login_window.geometry("300x150")

    login_label = tk.Label(login_window, text="Login", font=("Helvetica", 24, "bold"))
    login_label.pack(pady=(10, 20))

    username_label = tk.Label(login_window, text="Email:")
    username_label.pack(anchor="w", padx=10)

    username_entry = ttk.Entry(login_window, font=("Helvetica", 14))
    username_entry.pack(padx=10)

    password_label = tk.Label(login_window, text="Password:")
    password_label.pack(anchor="w", padx=10)

    password_entry = ttk.Entry(login_window, font=("Helvetica", 14), show="*")
    password_entry.pack(padx=10)

    login_button = ttk.Button(login_window, text="Login", command=login)
    login_button.pack(pady=20)
    login_window.mainloop()



# Create the login window
login_window = tk.Tk()
login_window.title("Login")
login_window.geometry("300x150")

login_label = tk.Label(login_window, text="Login", font=("Helvetica", 24, "bold"))
login_label.pack(pady=(10, 20))

username_label = tk.Label(login_window, text="Email:")
username_label.pack(anchor="w", padx=10)

username_entry = ttk.Entry(login_window, font=("Helvetica", 14))
username_entry.pack(padx=10)

password_label = tk.Label(login_window, text="Password:")
password_label.pack(anchor="w", padx=10)

password_entry = ttk.Entry(login_window, font=("Helvetica", 14), show="*")
password_entry.pack(padx=10)

login_button = ttk.Button(login_window, text="Login", command=login)
login_button.pack(pady=20)


# Function to open the main inventory window
def open_main_window():
    global shoe_data, cart, inventory_data
    inventory_data = get_shoeventory(user_id, token)  # Replace '1' with the merchant ID
    shoe_data = inventory_data[0]['shoes']  # Access the list of shoes from the API response
    cart = []

    # Rest of your code for the main inventory window

# Call the main loop for the login window
login_window.mainloop()


def close_main_window():
    root.destroy()


def update_total_amount():
    total_amount = sum(shoe["shoeQuantity"] * shoe["shoePrice"] for shoe in cart)
    PurchaseTotalTextBlock.delete(0, tk.END)
    PurchaseTotalTextBlock.insert(0, f"${total_amount}")


def add_to_cart():
    shoe_id = int(BarcodeTextBox.get())
    for shoe in cart:
        if shoe["id"] == shoe_id:
            # Increase quantity if the same shoe is added again
            shoe["shoeQuantity"] += 1
            break
    else:
        # Add a new shoe to the cart with initial quantity 1
        for shoe in shoe_data:
            if shoe["id"] == shoe_id:
                new_shoe = shoe.copy()
                new_shoe["shoeQuantity"] = 1
                cart.append(new_shoe)
                break
    InventoryListBox.delete(*InventoryListBox.get_children())
    for shoe in cart:
        InventoryListBox.insert("", tk.END, values=(shoe["id"],
                                                    shoe["manufacturer"],
                                                    shoe["shoeType"],
                                                    shoe["shoeName"],
                                                    shoe["shoeSize"],
                                                    shoe["shoeColor"],
                                                    shoe["shoeQuantity"],
                                                    shoe["shoePrice"]))
    update_total_amount()


def remove_from_cart():
    selected_item = InventoryListBox.selection()
    if selected_item:
        item_index = InventoryListBox.index(selected_item)
        shoe = cart[item_index]
        if shoe["shoeQuantity"] > 1:
            shoe["shoeQuantity"] -= 1
        else:
            del cart[item_index]
        InventoryListBox.delete(selected_item)
        update_total_amount()


def checkout():
    if not cart:
        messagebox.showinfo("Empty Cart", "Your cart is empty. Add items before checking out.")
        return

    response = messagebox.askyesno("Confirm Checkout", "Are you sure you want to checkout?")

    if response:
        create_transaction(user_id, cart)
        for shoe in cart:
            add_shoe_to_excel(shoe)

        # Clear the cart and update the total amount display
        clear_cart()
        messagebox.showinfo("Checkout Success", "Transaction completed successfully!")
    else:
        messagebox.showinfo("Checkout Canceled", "Checkout process canceled.")


def display_inventory():
    PosModePanel.pack_forget()  # Hide POS mode components
    InventoryModePanel.pack()  # Show Inventory mode components
    InventoryListBox.delete(*InventoryListBox.get_children())  # Clear the cart view when switching to Inventory mode
    data = shoe_data
    if data:
        for shoe in data:
            InventoryListBox.insert("", tk.END, values=(
                shoe["id"],
                shoe["manufacturer"],
                shoe["shoeType"],
                shoe["shoeName"],
                shoe["shoeSize"],
                shoe["shoeColor"],
                shoe["shoeQuantity"],
                shoe["shoePrice"]))


def back_to_pos():
    PosModePanel.pack()  # Show POS mode components
    InventoryModePanel.pack_forget()  # Hide Inventory mode components
    clear_inventory()


def remove_from_cart_single():
    shoe_id = int(BarcodeTextBox.get())
    found_shoe = None

    # Find the corresponding shoe in the cart
    for shoe in cart:
        if shoe["id"] == shoe_id:
            found_shoe = shoe
            if shoe["shoeQuantity"] > 1:
                shoe["shoeQuantity"] -= 1
            else:
                cart.remove(shoe)  # Remove the shoe from the cart if quantity is zero
            break

    if found_shoe is not None:
        # Remove the original entry from the cart
        InventoryListBox.delete(*InventoryListBox.get_children())

        # Update the table with the updated cart items
        for shoe in cart:
            InventoryListBox.insert("", tk.END, values=(
                shoe["id"],
                shoe["manufacturer"],
                shoe["shoeType"],
                shoe["shoeName"],
                shoe["shoeSize"],
                shoe["shoeColor"],
                shoe["shoeQuantity"],
                shoe["shoePrice"]))

        # Update the total amount after removing the shoe
        update_total_amount()

    else:
        # Inform the user that the shoe ID is not found in the cart
        messagebox.showinfo("Not Found", f"Shoe with ID {shoe_id} not found in the cart.")


# Function to switch to Inventory mode
def show_inventory():
    PosModePanel.pack_forget()  # Hide POS components
    InventoryModePanel.pack()  # Show Inventory components
    clear_cart()  # Clear the cart view when switching to Inventory mode
    display_inventory()


# Function to switch back to POS mode
def back_to_pos():
    InventoryModePanel.pack_forget()  # Hide Inventory components
    PosModePanel.pack()  # Show POS components
    clear_inventory()  # Clear the inventory view when switching to POS mode


# Function to clear the cart (POS mode)
def clear_cart():
    cart.clear()
    InventoryListBox.delete(*InventoryListBox.get_children())
    update_total_amount()


def clear_inventory():
    InventoryListBox.delete(*InventoryListBox.get_children())


# Select and set the collection to view
def set_collectionInventory(index):
    global shoe_data
    shoe_data = inventory_data[index]['shoes']
    clear_inventory()
    display_inventory()


root = tk.Tk()
root.title("Shoe Store Inventory")
root.geometry("800x450")

style = ttk.Style()
style.configure("TButton", background="#0078D7", foreground="white", font=("Helvetica", 14), padding=10)

header = tk.Label(root, text="Shoe Store Inventory", font=("Helvetica", 24, "bold"), foreground="black")
header.grid(row=0, column=0, pady=(10, 0))

main_content = tk.Frame(root, background="#F7F7F7")
main_content.grid(row=1, column=0, padx=40, pady=40, sticky="nsew")

columns = ("id", "manufacturer", "shoeType" , "shoeName", "shoeSize", "shoeColor", "shoeQuantity", "shoePrice")
InventoryListBox = ttk.Treeview(main_content, columns=columns, show="headings", selectmode="browse")
for col in columns:
    InventoryListBox.heading(col, text=col)
InventoryListBox.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

scrollbar = ttk.Scrollbar(main_content, orient="vertical", command=InventoryListBox.yview)
InventoryListBox.configure(yscrollcommand=scrollbar.set)
scrollbar.grid(row=0, column=1, sticky="ns")

actions_panel = tk.Frame(main_content, background="white")
actions_panel.grid(row=0, column=2, padx=(10, 0), sticky="nsew")

# POS Mode Interface
PosModePanel = tk.Frame(actions_panel)
PosModePanel.pack(padx=10, pady=(0, 20), fill="x")

BarcodeLabel = ttk.Label(PosModePanel, text="Scan Barcode ID:")
BarcodeLabel.pack(anchor="w", pady=(0, 5))

BarcodeTextBox = ttk.Entry(PosModePanel, font=("Helvetica", 14), width=20)
BarcodeTextBox.pack(pady=(0, 10))

AddToCartButton = ttk.Button(PosModePanel, text="Add to cart", command=add_to_cart)
AddToCartButton.pack(pady=10)

RemoveFromCartButton = ttk.Button(PosModePanel, text="Remove from cart", command=remove_from_cart_single)
RemoveFromCartButton.pack(pady=10)

CheckoutSection = ttk.LabelFrame(PosModePanel, text="Checkout", labelanchor="n")
CheckoutSection.pack(pady=20, padx=10, fill="x")

TotalPurchaseLabel = ttk.Label(CheckoutSection, text="Total Purchase:", font=("Helvetica", 18, "bold"))
TotalPurchaseLabel.pack(pady=(0, 5))

PurchaseTotalTextBlock = ttk.Entry(CheckoutSection, font=("Helvetica", 16, "bold"), width=20)
PurchaseTotalTextBlock.pack(pady=10)

collection_panel = tk.Frame(main_content, background="white")
collection_panel.grid(row=1, column=0, padx=(0, 10), pady=(20, 0), sticky="nsew")

# Dropdown to select collection to view
CollectionSelectPanel = tk.Frame(collection_panel)
CollectionSelectPanel.pack(pady=(0, 10))

options = []
for collection in inventory_data:
    options.append(collection["shoeCollectionName"])

CollectionSelectLabel = ttk.Label(CollectionSelectPanel, text="Select Collection:")
CollectionSelectLabel.pack(side="left", padx=(0, 10))

CollectionSelect = ttk.Combobox(CollectionSelectPanel, values=options, state="readonly")
CollectionSelect.pack(side="left")

CollectionSelect.bind("<<ComboboxSelected>>", lambda event: set_collectionInventory(CollectionSelect.current()))


ActionButton = ttk.Button(CheckoutSection, text="Checkout", command=checkout)
ActionButton.pack(pady=10)

# Inventory Mode Interface
InventoryModePanel = tk.Frame(actions_panel)

# Buttons to switch between modes
ModeButtonsFrame = tk.Frame(actions_panel)

ShowInventoryButton = ttk.Button(ModeButtonsFrame, text="Show Inventory", command=show_inventory)
ShowInventoryButton.pack(side="left", padx=10)

BackToPOSButton = ttk.Button(ModeButtonsFrame, text="Back to POS", command=back_to_pos)
BackToPOSButton.pack(side="left", padx=10)

LogoutButton = ttk.Button(ModeButtonsFrame, text="Logout", command=logout)
LogoutButton.pack(side="left", padx=10)

ModeButtonsFrame.pack()  # Pack the mode buttons frame

root.mainloop()