import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import mysql.connector
from PIL import Image, ImageTk
import urllib.request, io
from tkinter import filedialog
import os
import shutil


# --- Global Styles ---
BG_COLOR = "#23272f"
FG_TEXT = "#c9d1d9"
ACCENT_COLOR = "#3af7cb"
BTN_TEXT_COLOR = "#23272f"
BTN_HOVER = "#32e0a1"
FONT_TITLE = ("Arial Rounded MT Bold", 24, "bold")
FONT_LABEL = ("Segoe UI", 11)
FONT_BTN = ("Segoe UI", 11, "bold")
FONT_HEADER = ("Segoe UI", 13, "bold")

# --- DB Connection (edit as needed) ---
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="DLSU1234!",
        database="keykart"
    )

# ---------------- LOGIN WINDOW ----------------
def login_window():
    def do_login(event=None):
        uname = entry_user.get().strip()
        pword = entry_pass.get().strip()
        if not uname or not pword:
            messagebox.showwarning("Input Required", "Please enter both username and password.")
            return
        try:
            conn = get_db()
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (uname, pword))
            user = cur.fetchone()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not connect to MySQL.\n\n{e}")
            return
        if user:
            root.withdraw()
            if user['role'] == 'admin':
                admin_panel(user, root)
            elif user['role'] == 'staff':
                staff_panel(user, root)
            else:
                shop_window(user, root)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    root = tk.Tk()
    root.title("KeyKart | Login")
    root.geometry("400x360")
    root.configure(bg=BG_COLOR)
    root.resizable(False, False)
    root.protocol("WM_DELETE_WINDOW", root.destroy)

    # Title
    tk.Label(root, text="🗝️ KeyKart", font=FONT_TITLE, fg=ACCENT_COLOR, bg=BG_COLOR).pack(pady=(30, 10))

    # Entry frame
    entry_frame = tk.Frame(root, bg=BG_COLOR)
    entry_frame.pack(pady=10)

    # Username
    tk.Label(entry_frame, text="Username", font=FONT_LABEL, fg=FG_TEXT, bg=BG_COLOR).grid(row=0, column=0, sticky="w", pady=(0, 2))
    entry_user = tk.Entry(entry_frame, font=("Segoe UI", 12), width=28, bg="#323946", fg="white", insertbackground="white", relief="flat")
    entry_user.grid(row=1, column=0, pady=(0, 12))
    entry_user.focus()

    # Password
    tk.Label(entry_frame, text="Password", font=FONT_LABEL, fg=FG_TEXT, bg=BG_COLOR).grid(row=2, column=0, sticky="w", pady=(0, 2))
    entry_pass = tk.Entry(entry_frame, font=("Segoe UI", 12), width=28, show="•", bg="#323946", fg="white", insertbackground="white", relief="flat")
    entry_pass.grid(row=3, column=0, pady=(0, 12))
    entry_pass.bind("<Return>", do_login)

    # Login Button
    login_btn = tk.Button(root, text="Sign In", font=FONT_BTN, bg=ACCENT_COLOR, fg=BTN_TEXT_COLOR,
                          width=24, bd=0, relief="ridge", activebackground=BTN_HOVER, command=do_login)
    login_btn.pack(pady=(10, 20))

    # Hint
    tk.Label(root, text="Demo accounts:\nadmin/admin123 | staff1/staffpass | gamer1/gamerpass",
             font=("Segoe UI", 9), fg="#8d9bac", bg=BG_COLOR).pack(side="bottom", pady=10)

    root.mainloop()

# ---------------- SHOP WINDOW (Customer) ----------------
def shop_window(user, parent_window=None):
    if parent_window:
        parent_window.withdraw()  # hide login while shop is open

    shop = tk.Toplevel()
    shop.title(f"KeyKart Shop - {user['username']}")
    shop.geometry("1000x700")
    shop.configure(bg=BG_COLOR)
    shop.protocol("WM_DELETE_WINDOW", lambda: (parent_window.destroy()))

    tk.Label(shop, text=f"Welcome, {user['username']}!", font=FONT_HEADER, fg=ACCENT_COLOR, bg=BG_COLOR).pack(pady=(15, 5))
    tk.Label(shop, text="Product Catalog", font=FONT_LABEL, fg=FG_TEXT, bg=BG_COLOR).pack()

    tree = ttk.Treeview(shop, columns=("ID", "Name", "Category", "Price", "Stock"), show="headings", height=10)
    for col in ("ID", "Name", "Category", "Price", "Stock"):
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=120)

    # Override the Price column heading with your desired initial label
    tree.heading("Price", text="Price (PHP)")

    tree.pack(pady=10)

    # --- Currency selector ---
    currency_var = tk.StringVar(value="price_php")
    currency_frame = tk.Frame(shop, bg=BG_COLOR)
    currency_frame.pack()
    tk.Label(currency_frame, text="Currency:", font=FONT_LABEL, fg=FG_TEXT, bg=BG_COLOR).pack(side="left", padx=5)
    currency_cb = ttk.Combobox(currency_frame, textvariable=currency_var,
                               values=["price_php", "price_usd", "price_krw"], state="readonly")
    currency_cb.pack(side="left", padx=5)

     # Update heading and refresh on change
    def update_price_heading(*args):
        current = currency_var.get()
        if current == "price_php":
            tree.heading("Price", text="Price (PHP)")
        elif current == "price_usd":
            tree.heading("Price", text="Price (USD)")
        elif current == "price_krw":
            tree.heading("Price", text="Price (KRW)")
        refresh_products()

    currency_var.trace_add("write", update_price_heading)

    # Quantity
    qty_frame = tk.Frame(shop, bg=BG_COLOR)
    qty_frame.pack()
    tk.Label(qty_frame, text="Quantity:", font=FONT_LABEL, fg=FG_TEXT, bg=BG_COLOR).pack(side="left", padx=5)
    simple_qty = tk.IntVar(value=1)
    tk.Spinbox(qty_frame, from_=1, to=50, textvariable=simple_qty, width=5).pack(side="left")

    # Buttons
    btn_frame = tk.Frame(shop, bg=BG_COLOR)
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="Add to Cart", bg=ACCENT_COLOR, fg=BTN_TEXT_COLOR,
              font=FONT_BTN, width=15, activebackground=BTN_HOVER,
              command=lambda: add_to_cart(tree, simple_qty, cart)).grid(row=0, column=0, padx=8)
    tk.Button(btn_frame, text="Checkout", bg=ACCENT_COLOR, fg=BTN_TEXT_COLOR,
              font=FONT_BTN, width=15, activebackground=BTN_HOVER,
              command=lambda: checkout(cart, user, tree)).grid(row=0, column=1, padx=8)
    tk.Button(shop, text="View Order History", bg="#f7d23a", fg="#23272f", font=FONT_BTN,
              activebackground="#3d84c6",
              command=lambda: show_order_history(user)).pack(pady=6)
    # Logout button
    tk.Button(
        shop, text="Logout", font=FONT_BTN, bg="#e84c4c", fg="white",
        activebackground="#c9302c",
        command=lambda: (shop.destroy(), parent_window.deiconify() if parent_window else login_window())
    ).pack(pady=10)

    cart = []

    def refresh_products():
    # clear existing rows
        for row in tree.get_children():
            tree.delete(row)
        # fetch new rows
        try:
            conn = get_db()
            cur = conn.cursor()
            price_col = currency_var.get()
            cur.execute(f"SELECT product_id, name, category, {price_col}, stock FROM products WHERE is_active=1")
            for row in cur.fetchall():
                tree.insert('', 'end', values=row)
            conn.close()
        except Exception as e:
            messagebox.showerror("DB Error", f"Failed to fetch products:\n{e}")


    def add_to_cart(tree, qty_var, cart_list):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Choose a product!")
            return
        pid, name, cat, price, stock = tree.item(selected[0])['values']
        qty = qty_var.get()
        if qty > stock:
            messagebox.showwarning("Stock", "Not enough stock!")
            return
        cart_list.append((pid, qty, price))
        messagebox.showinfo("Added", f"Added {qty} of {name} to cart.")

    def checkout(cart_list, user, tree):
        if not cart_list:
            messagebox.showwarning("Cart", "Cart is empty!")
            return
        try:
            conn = get_db()
            cur = conn.cursor()
            for item in cart_list:
                cur.callproc('sp_place_order', (user['user_id'], item[0], item[1]))
            conn.commit()
            conn.close()
            cart_list.clear()
            messagebox.showinfo("Order", "Order placed! Check your email for delivery info.")
            refresh_products()
        except Exception as e:
            messagebox.showerror("Checkout Failed", str(e))

    refresh_products()
    shop.mainloop()

# ---------------- ORDER HISTORY ----------------
def show_order_history(user):
    history = tk.Toplevel()
    history.title("Order History")
    history.geometry("700x400")
    history.configure(bg=BG_COLOR)

    tk.Label(history, text="Your Orders", font=FONT_HEADER, fg=ACCENT_COLOR, bg=BG_COLOR).pack(pady=8)

    tree = ttk.Treeview(history, columns=("OrderID", "Date", "Total", "Status"), show="headings", height=10)
    for col in ("OrderID", "Date", "Total", "Status"):
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=150)
    tree.pack(pady=8)
    tk.Button(history, text="Cancel Selected Order", bg="#e84c4c", fg="white", font=FONT_BTN, activebackground="#c9302c",
              command=lambda: cancel_order(tree, user, load_orders)).pack(pady=6)

    def load_orders():
        for row in tree.get_children():
            tree.delete(row)
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT order_id, order_date, total_php, status FROM orders WHERE user_id=%s", (user['user_id'],))
        for row in cur.fetchall():
            tree.insert('', 'end', values=row)
        conn.close()

    def show_order_items(event):
        selected = tree.selection()
        if not selected:
            return
        order_id = tree.item(selected[0])['values'][0]
        items_win = tk.Toplevel(history)
        items_win.title(f"Order #{order_id} Items")
        items_win.geometry("650x300")
        tk.Label(items_win, text=f"Order #{order_id} - Items & Keys", font=FONT_HEADER).pack(pady=8)
        tree_items = ttk.Treeview(items_win, columns=("Product", "Qty", "Price", "Key"), show="headings")
        for col in ("Product", "Qty", "Price", "Key"):
            tree_items.heading(col, text=col)
            tree_items.column(col, width=140)
        tree_items.pack(fill="both", expand=True, pady=5)
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT p.name, oi.qty, oi.price_at_purchase, kd.game_key
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            LEFT JOIN key_deliveries kd ON kd.order_item_id = oi.order_item_id
            WHERE oi.order_id=%s
        """, (order_id,))
        for row in cur.fetchall():
            tree_items.insert('', 'end', values=row)
        conn.close()

    tree.bind("<<TreeviewSelect>>", show_order_items)
    load_orders()

def cancel_order(tree, user, refresh_func):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Select", "Choose an order to cancel.")
        return
    order_data = tree.item(selected[0])['values']
    order_id, _, _, status = order_data

    if status.lower() != "pending":
        messagebox.showinfo("Not Allowed", f"Only pending orders can be cancelled. Order #{order_id} is '{status}'.")
        return

    if messagebox.askyesno("Cancel Order", f"Are you sure you want to cancel Order #{order_id}?"):
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.callproc('sp_cancel_order', (order_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Cancelled", f"Order #{order_id} has been cancelled.")
            refresh_func()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to cancel order:\n{e}")



# ---------------- ADMIN PANEL ----------------
def admin_panel(user, parent_window):
    parent_window.withdraw()

    admin = tk.Toplevel(parent_window)
    admin.title(f"Admin Panel - {user['username']}")
    admin.geometry("700x500")
    admin.configure(bg=BG_COLOR)
    admin.protocol("WM_DELETE_WINDOW", lambda: parent_window.destroy())

    tk.Label(admin, text="Admin Panel", font=FONT_HEADER, fg=ACCENT_COLOR, bg=BG_COLOR).pack(pady=20)

    tk.Button(admin,
            text="Manage Product Inventory",
            font=FONT_BTN, width=30, bg="#4ee06e", fg=BTN_TEXT_COLOR,
            activebackground="#3ac454",
            command=lambda: open_inventory_view(admin, user)).pack(pady=10)

    tk.Button(admin,
            text="Manage User Roles",
            font=FONT_BTN, width=30, bg="#3da6f0", fg="white",
            activebackground="#2b8ad4",
            command=lambda: open_user_roles_window(admin, user)).pack(pady=10)


    # Logout button: close admin window and show login again
    tk.Button(
        admin, text="Logout", font=FONT_BTN, bg="#e84c4c", fg="white",
        activebackground="#c9302c",
        command=lambda: (admin.destroy(), parent_window.deiconify() if parent_window else login_window())
    ).pack(pady=10)

    
def open_inventory_view(admin_window, user):
    admin_window.withdraw()
    inventory_win = tk.Toplevel(admin_window)
    inventory_win.title("Product Inventory")
    inventory_win.geometry("1000x700")
    inventory_win.configure(bg=BG_COLOR)
    inventory_win.protocol("WM_DELETE_WINDOW", lambda: (inventory_win.destroy(), admin_window.deiconify()))

    tk.Label(inventory_win, text="Product Inventory", font=FONT_HEADER,
             fg=ACCENT_COLOR, bg=BG_COLOR).pack(pady=10)

    # Table
    tree = ttk.Treeview(inventory_win,
                        columns=("ID", "Name", "Category", "Price", "Stock"),
                        show="headings", height=12)
    for col in ("ID", "Name", "Category", "Price", "Stock"):
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=120)
    tree.pack(pady=8)

    # Currency selector
    currency_var = tk.StringVar(value="price_php")
    currency_frame = tk.Frame(inventory_win, bg=BG_COLOR)
    currency_frame.pack()
    tk.Label(currency_frame, text="Currency:", font=FONT_LABEL,
             fg=FG_TEXT, bg=BG_COLOR).pack(side="left", padx=5)
    currency_cb = ttk.Combobox(currency_frame, textvariable=currency_var,
                               values=["price_php", "price_usd", "price_krw"],
                               state="readonly")
    currency_cb.pack(side="left", padx=5)

    # Refresh function
    def refresh(tree_widget):
        tree_widget.delete(*tree_widget.get_children())
        try:
            conn = get_db()
            cur = conn.cursor()
            price_col = currency_var.get()
            cur.execute(f"SELECT product_id, name, category, {price_col}, stock FROM products WHERE is_active=1")
            for row in cur.fetchall():
                tree_widget.insert('', 'end', values=row)
            conn.close()
        except Exception as e:
            messagebox.showerror("DB Error", f"Failed to fetch products:\n{e}")

    # Update heading when currency changes
    def update_price_heading(*_):
        current = currency_var.get()
        if current == "price_php":
            tree.heading("Price", text="Price (PHP)")
        elif current == "price_usd":
            tree.heading("Price", text="Price (USD)")
        elif current == "price_krw":
            tree.heading("Price", text="Price (KRW)")
        refresh(tree)

    currency_var.trace_add("write", update_price_heading)

    # Popup for details
    def show_product_popup(event):
        selected = tree.selection()
        if not selected:
            return
        pid = tree.item(selected[0])['values'][0]
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("""SELECT name, category, description,
                                  price_php, price_usd, price_krw, stock, image_url
                           FROM products WHERE product_id=%s""", (pid,))
            result = cur.fetchone()
            conn.close()
        except Exception as e:
            messagebox.showerror("DB Error", f"Failed to fetch product:\n{e}")
            return

        if not result:
            return

        name, category, desc, php, usd, krw, stock, image_url = result
        popup = tk.Toplevel(inventory_win)
        popup.title(name)
        popup.geometry("400x500")
        popup.configure(bg=BG_COLOR)

        tk.Label(popup, text=name, font=FONT_HEADER, fg=ACCENT_COLOR, bg=BG_COLOR).pack(pady=10)
        tk.Label(popup, text=f"Category: {category}", font=FONT_LABEL, fg=FG_TEXT, bg=BG_COLOR).pack(pady=2)
        tk.Label(popup, text=f"Description: {desc}", font=FONT_LABEL, fg=FG_TEXT,
                 bg=BG_COLOR, wraplength=380, justify="left").pack(pady=2)
        tk.Label(popup, text=f"Price (PHP): {php}", font=FONT_LABEL, fg=FG_TEXT, bg=BG_COLOR).pack(pady=2)
        tk.Label(popup, text=f"Price (USD): {usd}", font=FONT_LABEL, fg=FG_TEXT, bg=BG_COLOR).pack(pady=2)
        tk.Label(popup, text=f"Price (KRW): {krw}", font=FONT_LABEL, fg=FG_TEXT, bg=BG_COLOR).pack(pady=2)
        tk.Label(popup, text=f"Stock: {stock}", font=FONT_LABEL, fg=FG_TEXT, bg=BG_COLOR).pack(pady=2)

        img_label = tk.Label(popup, bg=BG_COLOR)
        img_label.pack(pady=10)

        try:
            if image_url:
                if image_url.startswith("http://") or image_url.startswith("https://"):
                    with urllib.request.urlopen(image_url) as u:
                        raw = u.read()
                    im = Image.open(io.BytesIO(raw))
                else:
                    if not os.path.isabs(image_url):
                        image_url = os.path.join(os.getcwd(), image_url)
                    im = Image.open(image_url)
                im = im.resize((150, 150))
                photo = ImageTk.PhotoImage(im)
                img_label.config(image=photo)
                img_label.image = photo
            else:
                img_label.config(text="No image available", fg="white")
        except Exception as e:
            img_label.config(text="Error loading image", fg="red")

    # Bind after function defined
    tree.bind("<Double-1>", show_product_popup)

    # Buttons frame
    btn_frame = tk.Frame(inventory_win, bg=BG_COLOR)
    btn_frame.pack(pady=8)
    tk.Button(btn_frame, text="Add Product", bg="#4ee06e", fg=BTN_TEXT_COLOR,
              font=FONT_BTN, activebackground="#3ac454",
              command=lambda: add_product(tree, refresh)).grid(row=0, column=0, padx=8)
    tk.Button(btn_frame, text="Edit Product", bg="#f7d23a", fg=BTN_TEXT_COLOR,
              font=FONT_BTN, activebackground="#e6b92e",
              command=lambda: edit_product(tree, refresh)).grid(row=0, column=1, padx=8)
    tk.Button(btn_frame, text="Delete Product", bg="#f7d23a", fg="#23272f",
              font=FONT_BTN, activebackground="#e84c4c",
              command=lambda: delete_product(tree, refresh)).grid(row=0, column=2, padx=8)

    # Stock update
    stock_frame = tk.Frame(inventory_win, bg=BG_COLOR)
    stock_frame.pack(pady=6)
    tk.Label(stock_frame, text="Set New Stock:", font=FONT_LABEL,
             fg=FG_TEXT, bg=BG_COLOR).pack(side="left", padx=4)
    simple_qty = tk.IntVar(value=1)
    tk.Spinbox(stock_frame, from_=0, to=999, textvariable=simple_qty,
               width=6).pack(side="left", padx=4)
    tk.Button(stock_frame, text="Update Stock", font=FONT_BTN,
              bg=ACCENT_COLOR, fg=BTN_TEXT_COLOR,
              activebackground=BTN_HOVER,
              command=lambda: update_stock(tree, simple_qty, user, refresh)).pack(side="left", padx=8)

    # Refresh button
    tk.Button(inventory_win, text="Refresh", font=FONT_BTN,
              bg="#e0e1ea", fg="#23272f",
              activebackground="#cacbd1",
              command=lambda: refresh(tree)).pack(pady=6)
    # Back button at the top
    tk.Button(inventory_win, text="Back to Admin Panel",
            font=FONT_BTN, bg="#e84c4c", fg="white",
            activebackground="#c9302c",
            command=lambda: (inventory_win.destroy(), admin_window.deiconify())
            ).pack(pady=5)
    # Initial load
    refresh(tree)


def open_user_roles_window(admin_window, user):
    admin_window.withdraw()
    win = tk.Toplevel(admin_window)
    win.title("Manage User Roles")
    win.geometry("600x500")
    win.configure(bg=BG_COLOR)
    win.protocol("WM_DELETE_WINDOW", lambda: (win.destroy(), admin_window.deiconify()))

    tk.Label(win, text="User Roles", font=FONT_HEADER, fg=ACCENT_COLOR, bg=BG_COLOR).pack(pady=10)

    
    tree = ttk.Treeview(win, columns=("UserID", "Username", "Email", "Role"), show="headings", height=12)
    for col in ("UserID", "Username", "Email", "Role"):
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=140)
    tree.pack(pady=10)

    def load_users():
        for row in tree.get_children():
            tree.delete(row)
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT user_id, username, email, role FROM users")
            for row in cur.fetchall():
                tree.insert('', 'end', values=row)
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load users:\n{e}")

    def prompt_role_change(current_role):
        from tkinter import Toplevel, Label, Button, StringVar
        from tkinter.ttk import Combobox

        role_window = Toplevel()
        role_window.title("Select New Role")
        role_window.geometry("300x150")
        role_window.grab_set()  # Modal window

        Label(role_window, text="Select New Role:").pack(pady=10)
        role_var = StringVar(value=current_role)
        roles = ["admin", "customer", "staff"]
        role_combo = Combobox(role_window, textvariable=role_var, values=roles, state="readonly")
        role_combo.pack(pady=5)

        def submit():
            role_window.destroy()

        Button(role_window, text="OK", command=submit).pack(pady=10)
        role_window.wait_window()
        return role_var.get()

    def change_role():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Choose a user.")
            return
        user_id, username, email, current_role = tree.item(selected[0])['values']
        new_role = prompt_role_change(current_role)
        if new_role and new_role != current_role:
            try:
                conn = get_db()
                cur = conn.cursor()
                cur.callproc("sp_manage_user_roles", (user_id, new_role))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", f"{username}'s role updated to '{new_role}'.")
                load_users()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to change role:\n{e}")

    tk.Button(win, text="Change Selected User's Role", font=FONT_BTN, bg=ACCENT_COLOR,
              fg=BTN_TEXT_COLOR, activebackground=BTN_HOVER, command=change_role).pack(pady=6)

    tk.Button(win, text="Back to Admin Panel",
              font=FONT_BTN, bg="#e84c4c", fg="white",
              activebackground="#c9302c",
              command=lambda: (win.destroy(), admin_window.deiconify())
              ).pack(pady=5)
    load_users()

# ---------------- STAFF PANEL ----------------
def staff_panel(user, parent_window=None):
    if parent_window:
        parent_window.withdraw()  # hide login while staff panel is open

    staff = tk.Toplevel()
    staff.title(f"Staff Panel - {user['username']}")
    staff.geometry("1000x700")
    staff.configure(bg=BG_COLOR)
    staff.protocol("WM_DELETE_WINDOW", lambda: (parent_window.destroy()))

    tk.Label(staff, text="Staff Panel - Inventory", font=FONT_HEADER, fg=ACCENT_COLOR, bg=BG_COLOR).pack(pady=10)

    tree = ttk.Treeview(staff, columns=("ID", "Name", "Category", "Price", "Stock"), show="headings", height=12)
    for col in ("ID", "Name", "Category", "Price", "Stock"):
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=120)
    tree.pack(pady=8)

    # Currency selector
    currency_var = tk.StringVar(value="price_php")
    currency_frame = tk.Frame(staff, bg=BG_COLOR)
    currency_frame.pack()
    tk.Label(currency_frame, text="Currency:", font=FONT_LABEL, fg=FG_TEXT, bg=BG_COLOR).pack(side="left", padx=5)
    currency_cb = ttk.Combobox(currency_frame, textvariable=currency_var,
                               values=["price_php", "price_usd", "price_krw"], state="readonly")
    currency_cb.pack(side="left", padx=5)

    def update_price_heading(*args):
        cur = currency_var.get()
        if cur == "price_php":
            tree.heading("Price", text="Price (PHP)")
        elif cur == "price_usd":
            tree.heading("Price", text="Price (USD)")
        elif cur == "price_krw":
            tree.heading("Price", text="Price (KRW)")
        refresh(tree)
    currency_var.trace_add("write", update_price_heading)

    def refresh(tree_widget):
        for row in tree_widget.get_children():
            tree_widget.delete(row)
        conn = get_db()
        cur = conn.cursor()
        price_col = currency_var.get()
        cur.execute(f"SELECT product_id, name, category, {price_col}, stock FROM products WHERE is_active=1")
        for row in cur.fetchall():
            tree_widget.insert('', 'end', values=row)
        conn.close()

    # Only update stock (no add/edit/delete)
    stock_frame = tk.Frame(staff, bg=BG_COLOR)
    stock_frame.pack(pady=6)
    tk.Label(stock_frame, text="Set New Stock:", font=FONT_LABEL, fg=FG_TEXT, bg=BG_COLOR).pack(side="left", padx=4)
    simple_qty = tk.IntVar(value=1)
    tk.Spinbox(stock_frame, from_=0, to=999, textvariable=simple_qty, width=6).pack(side="left", padx=4)
    tk.Button(stock_frame, text="Update Stock", font=FONT_BTN, bg=ACCENT_COLOR, fg=BTN_TEXT_COLOR,
              activebackground=BTN_HOVER,
              command=lambda: update_stock(tree, simple_qty, user, refresh)).pack(side="left", padx=8)

    tk.Button(staff, text="Refresh", font=FONT_BTN, bg="#e0e1ea", fg="#23272f",
              activebackground="#cacbd1", command=lambda: refresh(tree)).pack(pady=6)
    tk.Button(
        staff, text="Logout", font=FONT_BTN, bg="#e84c4c", fg="white",
        activebackground="#c9302c",
        command=lambda: (staff.destroy(), parent_window.deiconify() if parent_window else login_window())
    ).pack(pady=10)


    refresh(tree)
    staff.mainloop()



# ---------------- Admin Helper Functions ----------------
def add_product(tree, refresh):
    win = tk.Toplevel()
    win.title("Add Product")
    win.geometry("420x420")
    fields = ["Name", "Category", "Price PHP", "Stock", "Description"]
    vars = [tk.StringVar() for _ in fields]
    image_path = tk.StringVar()
    categories = ['game_key', 'in_game_currency', 'merch']

    for i, label in enumerate(fields):
        tk.Label(win, text=label).grid(row=i, column=0, sticky='e', pady=5)
        if label == "Category":
            cb = ttk.Combobox(win, textvariable=vars[i], values=categories, state="readonly")
            cb.grid(row=i, column=1, pady=5)
        else:
            tk.Entry(win, textvariable=vars[i]).grid(row=i, column=1, pady=5)

    # ---------------- IMAGE UPLOAD FIELD ----------------
    image_path = tk.StringVar()
    tk.Label(win, text="Product Image").grid(row=len(fields), column=0, sticky='e', pady=5, padx=5)

    img_frame = tk.Frame(win)
    img_frame.grid(row=len(fields), column=1, pady=5)

    img_label = tk.Label(img_frame, text="No image selected", width=25, anchor="w")
    img_label.pack(side="left")

    def upload_image():
        from tkinter import filedialog
        import os, shutil
        file = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
        if file:
            filename = os.path.basename(file)
            # store in assets/images
            dest_dir = os.path.join(os.getcwd(), "assets", "images")
            os.makedirs(dest_dir, exist_ok=True)
            dest_path = os.path.join(dest_dir, filename)
            shutil.copy(file, dest_path)
            rel_path = os.path.relpath(dest_path, os.getcwd())
            image_path.set(rel_path)
            img_label.config(text=filename)

    tk.Button(img_frame, text="Browse", command=upload_image).pack(side="right")
    # ---------------- END IMAGE UPLOAD ------------------

    # save to database
    def save():
        try:
            # read the PHP price from the form
            php_price = float(vars[2].get())
        except ValueError:
            messagebox.showerror("Error", "Price PHP must be a valid number.")
            return

        usd_rate = 58.0   # 1 USD = 58 PHP
        krw_rate = 23.6   # 1 PHP = 23.6 KRW

        # Auto‑convert to USD and KRW
        usd_price = round(php_price / usd_rate, 2)
        krw_price = round(php_price * krw_rate, 0)

        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("""INSERT INTO products
                (name, category, price_php, price_usd, price_krw, stock, description, image_url)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                (vars[0].get(),            # name
                 vars[1].get(),            # category
                 php_price,                # price_php
                 usd_price,                # auto price_usd
                 krw_price,                # auto price_krw
                 vars[3].get(),            # stock
                 vars[4].get(),            # description
                 image_path.get()))        # image_url
            conn.commit()
            conn.close()
            messagebox.showinfo("Saved", "Product added successfully!")
            win.destroy()
            refresh(tree)
        except Exception as e:
            messagebox.showerror("Error", f"Could not add product:\n{e}")

    tk.Button(win, text="Save", bg="#4ee06e", fg=BTN_TEXT_COLOR,
              command=save).grid(row=len(fields)+1, column=1, pady=14)

    
def edit_product(tree, refresh):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Select", "Choose a product!")
        return
    pid, name, cat, price_php, stock = tree.item(selected[0])['values']
    win = tk.Toplevel()
    win.title("Edit Product")
    win.geometry("420x280")
    tk.Label(win, text="Name").grid(row=0, column=0, sticky='e', pady=5)
    name_var = tk.StringVar(value=name)
    tk.Entry(win, textvariable=name_var).grid(row=0, column=1, pady=5)
    tk.Label(win, text="Stock").grid(row=1, column=0, sticky='e', pady=5)
    stock_var = tk.StringVar(value=str(stock))
    tk.Entry(win, textvariable=stock_var).grid(row=1, column=1, pady=5)

    def save_edit():
        conn = get_db()
        cur = conn.cursor()
        cur.execute("UPDATE products SET name=%s, stock=%s WHERE product_id=%s",
                    (name_var.get(), stock_var.get(), pid))
        conn.commit()
        conn.close()
        win.destroy()
        refresh(tree)

    tk.Button(win, text="Save", bg="#4ee06e", fg=BTN_TEXT_COLOR, command=save_edit).grid(row=3, column=1, pady=14)

def delete_product(tree, refresh):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Select", "Choose a product!")
        return
    pid = tree.item(selected[0])['values'][0]
    if messagebox.askyesno("Archive Product", "Are you sure you want to archive this product? It will no longer appear in the shop."):
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("UPDATE products SET is_active = 0 WHERE product_id=%s", (pid,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Archived", "Product archived successfully!")
            refresh(tree)
        except Exception as e:
            messagebox.showerror("Error", f"Could not archive product:\n{e}")


def update_stock(tree, qty_var, user, refresh):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Select", "Choose a product!")
        return
    pid = tree.item(selected[0])['values'][0]
    new_stock = qty_var.get()
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.callproc('sp_update_stock', (pid, new_stock, user['user_id']))
        conn.commit()
        conn.close()
        messagebox.showinfo("Stock", "Stock updated!")
        refresh(tree)
    except Exception as e:
        messagebox.showerror("Error", f"Could not update stock:\n{e}")

# ---- RUN LOGIN ----
if __name__ == "__main__":
    login_window()
