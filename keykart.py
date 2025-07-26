import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import mysql.connector
# from PIL import Image, ImageTk
import urllib.request, io
from tkinter import filedialog
import os
import shutil
import datetime
import tempfile
import webbrowser


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
        password="p@ssword",
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
            # ✅ Only fetch users that are active
            cur.execute(
                "SELECT * FROM users WHERE username=%s AND password=%s AND is_active=1",
                (uname, pword)
            )
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
            messagebox.showerror("Login Failed", "Invalid username or password, or account is inactive.")


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

    tk.Button(root, text="Create New Account", font=FONT_BTN, bg="#3da6f0", fg="white",
          activebackground="#2b8ad4",
          width=24, bd=0, relief="ridge",
          command=lambda: registration_window(root)).pack(pady=(0, 10))


    # Hint
    tk.Label(root, text="Demo accounts:\nadmin/admin123 | staff1/staffpass | gamer1/gamerpass",
             font=("Segoe UI", 9), fg="#8d9bac", bg=BG_COLOR).pack(side="bottom", pady=10)

    root.mainloop()

# ---------------- REGISTER WINDOW ----------------
def registration_window(parent_window=None):
    if parent_window:
        parent_window.withdraw()

    reg = tk.Toplevel()
    reg.title("KeyKart | Register")
    reg.geometry("400x480")
    reg.configure(bg=BG_COLOR)
    reg.resizable(False, False)
    reg.protocol("WM_DELETE_WINDOW", lambda: (reg.destroy(), parent_window.deiconify() if parent_window else None))

    tk.Label(reg, text="📝 Create Account", font=FONT_TITLE, fg=ACCENT_COLOR, bg=BG_COLOR).pack(pady=(30, 10))

    form_frame = tk.Frame(reg, bg=BG_COLOR)
    form_frame.pack(pady=10)

    # Username
    tk.Label(form_frame, text="Username", font=FONT_LABEL, fg=FG_TEXT, bg=BG_COLOR).grid(row=0, column=0, sticky="w", pady=(0, 2))
    entry_user = tk.Entry(form_frame, font=("Segoe UI", 12), width=28, bg="#323946", fg="white", insertbackground="white", relief="flat")
    entry_user.grid(row=1, column=0, pady=(0, 12))

    # Email
    tk.Label(form_frame, text="Email", font=FONT_LABEL, fg=FG_TEXT, bg=BG_COLOR).grid(row=2, column=0, sticky="w", pady=(0, 2))
    entry_email = tk.Entry(form_frame, font=("Segoe UI", 12), width=28, bg="#323946", fg="white", insertbackground="white", relief="flat")
    entry_email.grid(row=3, column=0, pady=(0, 12))

    # Password
    tk.Label(form_frame, text="Password", font=FONT_LABEL, fg=FG_TEXT, bg=BG_COLOR).grid(row=4, column=0, sticky="w", pady=(0, 2))
    entry_pass = tk.Entry(form_frame, font=("Segoe UI", 12), width=28, show="•", bg="#323946", fg="white", insertbackground="white", relief="flat")
    entry_pass.grid(row=5, column=0, pady=(0, 12))

    # Confirm Password
    tk.Label(form_frame, text="Confirm Password", font=FONT_LABEL, fg=FG_TEXT, bg=BG_COLOR).grid(row=6, column=0, sticky="w", pady=(0, 2))
    entry_pass2 = tk.Entry(form_frame, font=("Segoe UI", 12), width=28, show="•", bg="#323946", fg="white", insertbackground="white", relief="flat")
    entry_pass2.grid(row=7, column=0, pady=(0, 12))

    def register_user():
        uname = entry_user.get().strip()
        email = entry_email.get().strip()
        pw1 = entry_pass.get().strip()
        pw2 = entry_pass2.get().strip()

        if not uname or not email or not pw1 or not pw2:
            messagebox.showwarning("Input Required", "All fields are required.")
            return
        if pw1 != pw2:
            messagebox.showerror("Password Mismatch", "Passwords do not match.")
            return

        try:
            conn = get_db()
            cur = conn.cursor()
            # check duplicates
            cur.execute("SELECT COUNT(*) FROM users WHERE username=%s OR email=%s", (uname, email))
            if cur.fetchone()[0] > 0:
                messagebox.showerror("Duplicate", "Username or email already exists.")
                conn.close()
                return
            # insert new user
            cur.execute("INSERT INTO users (username, password, email, role) VALUES (%s, %s, %s, 'customer')",
                        (uname, pw1, email))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Account created! You can now log in.")
            reg.destroy()
            if parent_window:
                parent_window.deiconify()
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not register user:\n{e}")

    tk.Button(reg, text="Register", font=FONT_BTN, bg=ACCENT_COLOR, fg=BTN_TEXT_COLOR,
              width=24, bd=0, relief="ridge", activebackground=BTN_HOVER,
              command=register_user).pack(pady=(10, 20))

    tk.Button(reg, text="Back to Login", font=FONT_BTN, bg="#e84c4c", fg="white",
              activebackground="#c9302c",
              command=lambda: (reg.destroy(), parent_window.deiconify() if parent_window else login_window())).pack(pady=5)
# ---------------- SHOP WINDOW (Customer) ----------------
def shop_window(user, parent_window=None):
    if parent_window:
        parent_window.withdraw()

    shop = tk.Toplevel()
    shop.title(f"KeyKart Shop - {user['username']}")
    shop.geometry("1100x750")
    shop.configure(bg=BG_COLOR)
    shop.protocol("WM_DELETE_WINDOW", lambda: (parent_window.destroy()))

    tk.Label(shop, text=f"Welcome, {user['username']}!", font=FONT_HEADER, fg=ACCENT_COLOR, bg=BG_COLOR).pack(pady=5)

    # --- Currency selector (shared) ---
    currency_var = tk.StringVar(value="price_php")
    currency_frame = tk.Frame(shop, bg=BG_COLOR)
    currency_frame.pack(pady=4)
    tk.Label(currency_frame, text="Currency:", font=FONT_LABEL, fg=FG_TEXT, bg=BG_COLOR).pack(side="left", padx=5)
    currency_cb = ttk.Combobox(currency_frame, textvariable=currency_var,
                               values=["price_php", "price_usd", "price_krw"], state="readonly")
    currency_cb.pack(side="left", padx=5)

    notebook = ttk.Notebook(shop)
    notebook.pack(fill="both", expand=True)

    # =============== Tab 1: Product Catalog ===============
    catalog_tab = tk.Frame(notebook, bg=BG_COLOR)
    notebook.add(catalog_tab, text="Product Catalog")

    tree = ttk.Treeview(catalog_tab, columns=("ID", "Name", "Category", "Price", "Stock"),
                        show="headings", height=12)
    for col in ("ID", "Name", "Category", "Price", "Stock"):
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=150)
    tree.pack(pady=10, fill="both", expand=True)

    qty_frame = tk.Frame(catalog_tab, bg=BG_COLOR)
    qty_frame.pack(pady=6)
    tk.Label(qty_frame, text="Quantity:", font=FONT_LABEL, fg=FG_TEXT, bg=BG_COLOR).pack(side="left", padx=4)
    simple_qty = tk.IntVar(value=1)
    tk.Spinbox(qty_frame, from_=1, to=50, textvariable=simple_qty, width=5).pack(side="left", padx=4)

    btn_frame = tk.Frame(catalog_tab, bg=BG_COLOR)
    btn_frame.pack(pady=6)
    tk.Button(btn_frame, text="Add to Cart", bg=ACCENT_COLOR, fg=BTN_TEXT_COLOR,
              font=FONT_BTN, width=15, activebackground=BTN_HOVER,
              command=lambda: add_to_cart(tree, simple_qty)).grid(row=0, column=0, padx=8)

    # =============== Tab 2: Cart ===============
    cart_tab = tk.Frame(notebook, bg=BG_COLOR)
    notebook.add(cart_tab, text="My Cart")

    cart_tree = ttk.Treeview(cart_tab, columns=("Name", "Qty", "Price", "Subtotal"),
                             show="headings", height=12)
    for col in ("Name", "Qty", "Price", "Subtotal"):
        cart_tree.heading(col, text=col)
        cart_tree.column(col, anchor="center", width=180)
    cart_tree.pack(pady=10, fill="both", expand=True)

    cart_total_label = tk.Label(cart_tab, text="Total: 0", font=FONT_LABEL, fg=FG_TEXT, bg=BG_COLOR)
    cart_total_label.pack(pady=5)

    # =============== Tab 3: Order History ===============
    history_tab = tk.Frame(notebook, bg=BG_COLOR)
    notebook.add(history_tab, text="Order History")

    orders_tree = ttk.Treeview(history_tab,
                               columns=("OrderID", "Products", "Date", "Total", "Status"),
                               show="headings", height=12)
    for col in ("OrderID", "Products", "Date", "Total", "Status"):
        orders_tree.heading(col, text=col)
        if col == "Products":
            orders_tree.column(col, anchor="w", width=250)
        else:
            orders_tree.column(col, anchor="center", width=120)
    orders_tree.pack(pady=10, fill="both", expand=True)

    tk.Button(history_tab, text="Cancel Selected Order", bg="#e84c4c", fg="white",
              font=FONT_BTN, activebackground="#c9302c",
              command=lambda: cancel_order(orders_tree, user, load_orders)).pack(pady=6)

    tk.Button(history_tab, text="Mark as Delivered", bg=ACCENT_COLOR, fg=BTN_TEXT_COLOR,
              font=FONT_BTN, activebackground=BTN_HOVER,
              command=lambda: mark_order_delivered(orders_tree)).pack(pady=6)

    # === Data structures ===
    cart = []  # (product_id, name, qty, price, category)

    # === Functions ===
    def refresh_products():
        tree.delete(*tree.get_children())
        conn = get_db()
        cur = conn.cursor()
        price_col = currency_var.get()
        cur.execute(f"SELECT product_id, name, category, {price_col}, stock FROM products WHERE is_active=1")
        for row in cur.fetchall():
            tree.insert('', 'end', values=row)
        conn.close()

    def update_cart_view():
        cart_tree.delete(*cart_tree.get_children())
        total = 0.0
        for item in cart:
            pname, qty, price = item[1], item[2], item[3]
            subtotal = qty * price
            total += subtotal
            cart_tree.insert("", "end", values=(pname, qty, f"{price:.2f}", f"{subtotal:.2f}"))
        cart_total_label.config(text=f"Total: {total:.2f}")

    def remove_from_cart():
        selected = cart_tree.selection()
        if not selected:
            messagebox.showwarning("Cart", "Select an item to remove.")
            return
        index = cart_tree.index(selected[0])
        cart.pop(index)
        update_cart_view()

    def add_to_cart(tree_widget, qty_var):
        selected = tree_widget.selection()
        if not selected:
            messagebox.showwarning("Select", "Choose a product!")
            return
        pid, name, cat, price_str, stock_str = tree_widget.item(selected[0])['values']
        try:
            price = float(price_str)
            stock = int(stock_str)
        except ValueError:
            messagebox.showerror("Data Error", "Invalid price or stock.")
            return
        qty = qty_var.get()
        if qty > stock:
            messagebox.showwarning("Stock", "Not enough stock!")
            return
        cart.append((pid, name, qty, price, cat))
        update_cart_view()
        messagebox.showinfo("Added", f"Added {qty} of {name} to cart.")

    def checkout(user, payment_method="Cash"):
        if not cart:
            messagebox.showwarning("Cart", "Cart is empty!")
            return
        try:
            conn = get_db()
            cur = conn.cursor()
            for item in cart:
                cur.callproc('sp_place_order', (user['user_id'], item[0], item[2]))
                # After placing order, handle status for digital vs merch
                cur.execute("SELECT LAST_INSERT_ID()")
                order_id = cur.fetchone()[0]
                if item[4] in ('game_key', 'in_game_currency'):
                    # Auto-complete for digital
                    cur.execute("UPDATE orders SET status='completed' WHERE order_id=%s", (order_id,))
                # merch stays pending
            # fetch latest orders for logging
            cur.execute("SELECT order_id, total_php FROM orders WHERE user_id=%s ORDER BY order_date DESC LIMIT %s",
                        (user['user_id'], len(cart)))
            orders_logged = cur.fetchall()
            for order_id, total_php in orders_logged:
                cur.execute("""
                INSERT INTO transaction_log (order_id, payment_method, payment_status, amount)
                VALUES (%s, %s, %s, %s)
            """, (order_id, payment_method, 'Paid', total_php))
            conn.commit()
            conn.close()
            cart.clear()
            update_cart_view()
            messagebox.showinfo("Order", "Order placed! Check your email for updates.")
            refresh_products()
            load_orders()
        except Exception as e:
            messagebox.showerror("Checkout Failed", str(e))

    def cancel_order(tree_widget, user, refresh_func):
        selected = tree_widget.selection()
        if not selected:
            messagebox.showwarning("Select", "Choose an order to cancel.")
            return
        order_data = tree_widget.item(selected[0])['values']
        order_id, _, _, _, status = order_data
        if str(status).lower() != "pending":
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

    def mark_order_delivered(tree_widget):
        selected = tree_widget.selection()
        if not selected:
            messagebox.showwarning("Select", "Choose an order to mark delivered.")
            return
        order_id, _, _, _, status = tree_widget.item(selected[0])['values']
        if str(status).lower() != "on_the_way":
            messagebox.showinfo("Not Allowed", f"Only 'On the Way' orders can be marked as delivered.")
            return
        if messagebox.askyesno("Mark as Delivered", f"Mark Order #{order_id} as delivered?"):
            try:
                conn = get_db()
                cur = conn.cursor()
                cur.execute("UPDATE orders SET status='completed' WHERE order_id=%s", (order_id,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Delivered", f"Order #{order_id} marked as Delivered.")
                load_orders()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to mark as delivered:\n{e}")

    def load_orders():
        orders_tree.delete(*orders_tree.get_children())
        conn = get_db()
        cur = conn.cursor()
        if currency_var.get() == "price_php":
            total_col = "total_php"
        elif currency_var.get() == "price_usd":
            total_col = "total_usd"
        else:
            total_col = "total_krw"
        query = f"""
            SELECT o.order_id,
                   GROUP_CONCAT(p.name SEPARATOR ', ') AS products,
                   o.order_date,
                   o.{total_col},
                   o.status
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN products p ON oi.product_id = p.product_id
            WHERE o.user_id=%s
            GROUP BY o.order_id, o.order_date, o.{total_col}, o.status
            ORDER BY o.order_date DESC
        """
        cur.execute(query, (user['user_id'],))
        for row in cur.fetchall():
            orders_tree.insert('', 'end', values=row)
        conn.close()

    def update_currency(*args):
        if currency_var.get() == "price_php":
            tree.heading("Price", text="Price (PHP)")
            orders_tree.heading("Total", text="Total (PHP)")
        elif currency_var.get() == "price_usd":
            tree.heading("Price", text="Price (USD)")
            orders_tree.heading("Total", text="Total (USD)")
        else:
            tree.heading("Price", text="Price (KRW)")
            orders_tree.heading("Total", text="Total (KRW)")
        refresh_products()
        load_orders()

    currency_var.trace_add("write", update_currency)

    # Initial load
    refresh_products()
    load_orders()

    # Cart tab buttons
    tk.Button(cart_tab, text="Remove Selected", bg="#e84c4c", fg="white",
              font=FONT_BTN, activebackground="#c9302c",
              command=remove_from_cart).pack(pady=6)
    payment_frame = tk.Frame(cart_tab, bg=BG_COLOR)
    payment_frame.pack(pady=6)
    tk.Label(payment_frame, text="Payment Method:", font=FONT_LABEL, fg=FG_TEXT, bg=BG_COLOR).pack(side="left", padx=4)
    payment_method_var = tk.StringVar(value="Cash")
    payment_cb = ttk.Combobox(payment_frame, textvariable=payment_method_var,
                              values=["Cash", "Credit Card", "GCash"], state="readonly")
    payment_cb.pack(side="left", padx=4)
    tk.Button(cart_tab, text="Checkout", bg=ACCENT_COLOR, fg=BTN_TEXT_COLOR,
              font=FONT_BTN, activebackground=BTN_HOVER,
              command=lambda: checkout(user, payment_method_var.get())).pack(pady=6)

    tk.Button(shop, text="Logout", font=FONT_BTN, bg="#e84c4c", fg="white",
              activebackground="#c9302c",
              command=lambda: (shop.destroy(), parent_window.deiconify() if parent_window else login_window())).pack(pady=10)

    shop.mainloop()


# ===================== ADMIN PANEL =====================

def admin_panel(user, parent_window):
    if parent_window:
        parent_window.withdraw()

    admin = tk.Toplevel(parent_window)
    admin.title(f"Admin Panel - {user['username']}")
    admin.geometry("1100x700")
    admin.configure(bg=BG_COLOR)
    admin.protocol("WM_DELETE_WINDOW", lambda: parent_window.destroy())

    tk.Label(admin, text=f"Admin Panel - Welcome {user['username']}",
             font=FONT_HEADER, fg=ACCENT_COLOR, bg=BG_COLOR).pack(pady=8)

    # Main container for notebook
    container = tk.Frame(admin, bg=BG_COLOR)
    container.pack(fill="both", expand=True)

    # Create Notebook
    notebook = ttk.Notebook(container)
    notebook.pack(fill="both", expand=True)

    # ===================== INVENTORY TAB =====================
    inventory_tab = tk.Frame(notebook, bg=BG_COLOR)
    notebook.add(inventory_tab, text="Manage Inventory")

    inv_tree = ttk.Treeview(inventory_tab,
                            columns=("ID", "Name", "Category", "Price", "Stock"),
                            show="headings", height=12)
    for col in ("ID", "Name", "Category", "Price", "Stock"):
        inv_tree.heading(col, text=col)
        inv_tree.column(col, anchor="center", width=120)
    inv_tree.pack(pady=8, fill="both", expand=True)

    currency_var = tk.StringVar(value="price_php")
    currency_frame = tk.Frame(inventory_tab, bg=BG_COLOR)
    currency_frame.pack()
    tk.Label(currency_frame, text="Currency:", font=FONT_LABEL, fg=FG_TEXT, bg=BG_COLOR).pack(side="left", padx=5)
    currency_cb = ttk.Combobox(currency_frame, textvariable=currency_var,
                               values=["price_php", "price_usd", "price_krw"],
                               state="readonly")
    currency_cb.pack(side="left", padx=5)

    def refresh_inventory():
        inv_tree.delete(*inv_tree.get_children())
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute(f"SELECT product_id, name, category, {currency_var.get()}, stock FROM products WHERE is_active=1")
            for row in cur.fetchall():
                inv_tree.insert('', 'end', values=row)
            conn.close()
        except Exception as e:
            messagebox.showerror("DB Error", f"Failed to fetch products:\n{e}")

    def update_price_heading(*_):
        current = currency_var.get()
        if current == "price_php":
            inv_tree.heading("Price", text="Price (PHP)")
        elif current == "price_usd":
            inv_tree.heading("Price", text="Price (USD)")
        else:
            inv_tree.heading("Price", text="Price (KRW)")
        refresh_inventory()

    currency_var.trace_add("write", update_price_heading)

    # Stock update controls
    stock_frame = tk.Frame(inventory_tab, bg=BG_COLOR)
    stock_frame.pack(pady=6)
    tk.Label(stock_frame, text="Set New Stock:", font=FONT_LABEL, fg=FG_TEXT, bg=BG_COLOR).pack(side="left", padx=4)
    qty_var = tk.IntVar(value=1)
    tk.Spinbox(stock_frame, from_=0, to=999, textvariable=qty_var, width=6).pack(side="left", padx=4)
    tk.Button(stock_frame, text="Update Stock", font=FONT_BTN,
              bg=ACCENT_COLOR, fg=BTN_TEXT_COLOR, activebackground=BTN_HOVER,
              command=lambda: update_stock(inv_tree, qty_var, user, refresh_inventory)).pack(side="left", padx=8)

    # Inventory Buttons
    inv_btn_frame = tk.Frame(inventory_tab, bg=BG_COLOR)
    inv_btn_frame.pack(pady=8)
    tk.Button(inv_btn_frame, text="Add Product", bg="#4ee06e", fg=BTN_TEXT_COLOR,
              font=FONT_BTN, activebackground="#3ac454",
              command=lambda: add_product(inv_tree, refresh_inventory)).grid(row=0, column=0, padx=8)
    tk.Button(inv_btn_frame, text="Edit Product", bg="#f7d23a", fg=BTN_TEXT_COLOR,
              font=FONT_BTN, activebackground="#e6b92e",
              command=lambda: edit_product(inv_tree, refresh_inventory)).grid(row=0, column=1, padx=8)
    tk.Button(inv_btn_frame, text="Delete Product", bg="#f7d23a", fg="#23272f",
              font=FONT_BTN, activebackground="#e84c4c",
              command=lambda: delete_product(inv_tree, refresh_inventory)).grid(row=0, column=2, padx=8)

    # ===================== TRANSACTION LOG TAB =====================
    transaction_tab = tk.Frame(notebook, bg=BG_COLOR)
    notebook.add(transaction_tab, text="Transaction Log")

    tk.Label(transaction_tab, text="Transaction Log",
             font=FONT_HEADER, fg=ACCENT_COLOR, bg=BG_COLOR).pack(pady=10)

    trans_tree = ttk.Treeview(
        transaction_tab,
        columns=("TransactionID", "OrderID", "Username", "Products", "Method", "Status", "Amount", "Generated"),
        show="headings", height=15
    )
    for col, width in zip(
        ("TransactionID", "OrderID", "Username", "Products", "Method", "Status", "Amount", "Generated"),
        (90, 80, 100, 200, 100, 100, 100, 160)
    ):
        trans_tree.heading(col, text=col)
        trans_tree.column(col, anchor="center", width=width)
    trans_tree.column("Products", anchor="w", width=220)
    trans_tree.pack(pady=8, fill="both", expand=True)

    # Date range UI
    sales_frame = tk.Frame(transaction_tab, bg=BG_COLOR)
    sales_frame.pack(pady=10)
    tk.Label(sales_frame, text="Sales report from (MM-DD-YYYY):",
             font=FONT_LABEL, fg=FG_TEXT, bg=BG_COLOR).pack(side="left", padx=6)

    start_month = tk.IntVar(value=1)
    start_day = tk.IntVar(value=1)
    start_year = tk.IntVar(value=2024)
    end_month = tk.IntVar(value=1)
    end_day = tk.IntVar(value=1)
    end_year = tk.IntVar(value=2024)

    for var in (start_month, start_day, start_year):
        tk.Spinbox(sales_frame, from_=1, to=12 if var == start_month else 31 if var == start_day else 3000,
                   textvariable=var, width=5).pack(side="left", padx=2)
    tk.Label(sales_frame, text=" to ", font=FONT_LABEL, fg=FG_TEXT, bg=BG_COLOR).pack(side="left", padx=6)
    for var in (end_month, end_day, end_year):
        tk.Spinbox(sales_frame, from_=1, to=12 if var == end_month else 31 if var == end_day else 3000,
                   textvariable=var, width=5).pack(side="left", padx=2)

    def load_transactions_filtered():
        start_date = datetime.date(start_year.get(), start_month.get(), start_day.get())
        end_date = datetime.date(end_year.get(), end_month.get(), end_day.get())
        if start_date > end_date:
            messagebox.showerror("Date Error", "Start date must be before end date.")
            return
        trans_tree.delete(*trans_tree.get_children())
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("""
                SELECT t.transaction_id, t.order_id, u.username,
                       GROUP_CONCAT(p.name SEPARATOR ', ') AS products,
                       t.payment_method, t.payment_status, t.amount, t.timestamp
                FROM transaction_log t
                JOIN orders o ON t.order_id = o.order_id
                JOIN users u ON o.user_id = u.user_id
                JOIN order_items oi ON o.order_id = oi.order_id
                JOIN products p ON oi.product_id = p.product_id
                WHERE DATE(t.timestamp) BETWEEN %s AND %s
                GROUP BY t.transaction_id, t.order_id, u.username, t.payment_method,
                         t.payment_status, t.amount, t.timestamp
                ORDER BY t.timestamp DESC
            """, (start_date, end_date))
            for row in cur.fetchall():
                trans_tree.insert('', 'end', values=row)
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load transactions:\n{e}")

    def print_transactions():
        rows = [trans_tree.item(i)['values'] for i in trans_tree.get_children()]
        if not rows:
            messagebox.showinfo("Print Report", "No data to print. Generate a report first.")
            return
        html = "<html><head><title>Transaction Report</title></head><body><h2>Transaction Report</h2><table border='1'>"
        html += "<tr>" + "".join(f"<th>{c}</th>" for c in ("TransactionID","OrderID","Username","Products","Method","Status","Amount","Generated")) + "</tr>"
        for r in rows:
            html += "<tr>" + "".join(f"<td>{v}</td>" for v in r) + "</tr>"
        html += "</table></body></html>"
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        temp.write(html.encode('utf-8')); temp.close()
        webbrowser.open(f"file://{temp.name}")
        messagebox.showinfo("Print Report", "Report opened in your browser. Press Ctrl+P to print.")

    tk.Button(sales_frame, text="Generate Report", font=FONT_BTN, bg=ACCENT_COLOR,
              fg=BTN_TEXT_COLOR, activebackground=BTN_HOVER,
              command=load_transactions_filtered).pack(side="left", padx=10)
    tk.Button(sales_frame, text="Print Report", font=FONT_BTN, bg="#4ee06e",
              fg=BTN_TEXT_COLOR, activebackground="#3ac454",
              command=print_transactions).pack(side="left", padx=10)

    # Initial load
    def load_all_transactions():
        trans_tree.delete(*trans_tree.get_children())
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("""
                SELECT t.transaction_id, t.order_id, u.username,
                       GROUP_CONCAT(p.name SEPARATOR ', ') AS products,
                       t.payment_method, t.payment_status, t.amount, t.timestamp
                FROM transaction_log t
                JOIN orders o ON t.order_id = o.order_id
                JOIN users u ON o.user_id = u.user_id
                JOIN order_items oi ON o.order_id = oi.order_id
                JOIN products p ON oi.product_id = p.product_id
                GROUP BY t.transaction_id, t.order_id, u.username, t.payment_method,
                         t.payment_status, t.amount, t.timestamp
                ORDER BY t.timestamp DESC
            """)
            for row in cur.fetchall():
                trans_tree.insert('', 'end', values=row)
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load transactions:\n{e}")

    load_all_transactions()


    # ===================== USER ROLES TAB =====================
    roles_tab = tk.Frame(notebook, bg=BG_COLOR)
    notebook.add(roles_tab, text="Manage User Roles")

    tk.Label(roles_tab, text="User Roles", font=FONT_HEADER, fg=ACCENT_COLOR, bg=BG_COLOR).pack(pady=10)
    user_tree = ttk.Treeview(roles_tab, columns=("UserID", "Username", "Email", "Role"), show="headings", height=12)
    for col in ("UserID", "Username", "Email", "Role"):
        user_tree.heading(col, text=col)
        user_tree.column(col, anchor="center", width=140)
    user_tree.pack(pady=8, fill="both", expand=True)

    def load_users():
        user_tree.delete(*user_tree.get_children())
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT user_id, username, email, role FROM users WHERE is_active=1")
            for row in cur.fetchall():
                user_tree.insert('', 'end', values=row)
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load users:\n{e}")

    def change_role():
        selected = user_tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Choose a user.")
            return
        uid, uname, email, current_role = user_tree.item(selected[0])['values']
        from tkinter import Toplevel, Label, Button, StringVar
        from tkinter.ttk import Combobox
        role_win = Toplevel(admin)
        role_win.title("Select New Role")
        role_win.geometry("300x150")
        role_win.grab_set()
        Label(role_win, text="Select New Role:").pack(pady=10)
        role_var = StringVar(value=current_role)
        roles = ["admin", "staff", "customer"]
        cb = Combobox(role_win, textvariable=role_var, values=roles, state="readonly")
        cb.pack(pady=5)
        def submit():
            new_role = role_var.get()
            if new_role and new_role != current_role:
                try:
                    conn = get_db()
                    cur = conn.cursor()
                    cur.callproc("sp_manage_user_roles", (uid, new_role))
                    conn.commit()
                    conn.close()
                    messagebox.showinfo("Success", f"{uname}'s role changed to {new_role}")
                    load_users()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to update role:\n{e}")
            role_win.destroy()
        Button(role_win, text="OK", command=submit).pack(pady=10)

    def delete_user():
        selected = user_tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Choose a user.")
            return
        uid = user_tree.item(selected[0])['values'][0]

        if messagebox.askyesno("Confirm", "Deactivate (soft delete) this user?"):
            try:
                conn = get_db()
                cur = conn.cursor()
                # archive details first
                cur.execute("""
                    INSERT INTO user_archive (user_id, username, email, role)
                    SELECT user_id, username, email, role FROM users WHERE user_id=%s
                """, (uid,))
                # mark as inactive
                cur.execute("UPDATE users SET is_active=0 WHERE user_id=%s", (uid,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Deactivated", "User deactivated (soft deleted) and archived.")
                load_users()
                load_archived_users()
            except Exception as e:
                messagebox.showerror("Error", f"Could not deactivate user:\n{e}")

    role_btn_frame = tk.Frame(roles_tab, bg=BG_COLOR)
    role_btn_frame.pack(pady=8)
    tk.Button(role_btn_frame, text="Change Role", font=FONT_BTN, bg=ACCENT_COLOR,
              fg=BTN_TEXT_COLOR, activebackground=BTN_HOVER,
              command=change_role).grid(row=0, column=0, padx=8)
    tk.Button(role_btn_frame, text="Delete User", font=FONT_BTN, bg="#ff9100",
              fg=BTN_TEXT_COLOR, activebackground="#e84c4c",
              command=delete_user).grid(row=0, column=1, padx=8)

# ===================== ARCHIVED USERS TAB =====================
    archived_tab = tk.Frame(notebook, bg=BG_COLOR)
    notebook.add(archived_tab, text="Archived Users")

    tk.Label(
        archived_tab,
        text="Archived Users",
        font=FONT_HEADER,
        fg=ACCENT_COLOR,
        bg=BG_COLOR
    ).pack(pady=10)

    archived_tree = ttk.Treeview(
        archived_tab,
        columns=("UserID", "Username", "Email", "Role", "ArchivedAt"),
        show="headings",
        height=12
    )
    for col in ("UserID", "Username", "Email", "Role", "ArchivedAt"):
        archived_tree.heading(col, text=col)
        archived_tree.column(col, anchor="center", width=140)
    archived_tree.pack(pady=8, fill="both", expand=True)

    def load_archived_users():
        archived_tree.delete(*archived_tree.get_children())
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT user_id, username, email, role, archived_at FROM user_archive ORDER BY archived_at DESC")
            for row in cur.fetchall():
                archived_tree.insert('', 'end', values=row)
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load archived users:\n{e}")

    def reactivate_user():
        selected = archived_tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Choose a user to reactivate.")
            return

        uid, uname, email, role, archived_at = archived_tree.item(selected[0])['values']

        if messagebox.askyesno("Reactivate", f"Reactivate user '{uname}'?"):
            try:
                conn = get_db()
                cur = conn.cursor()
                # ✅ Set is_active back to 1
                cur.execute("UPDATE users SET is_active = 1 WHERE user_id = %s", (uid,))
                # ✅ Remove from archive
                cur.execute("DELETE FROM user_archive WHERE user_id = %s", (uid,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Reactivated", f"User '{uname}' has been reactivated.")
                load_archived_users()
                load_users()
            except Exception as e:
                messagebox.showerror("Error", f"Could not reactivate user:\n{e}")

    # Frame for reactivate button
    reactivate_btn_frame = tk.Frame(archived_tab, bg=BG_COLOR)
    reactivate_btn_frame.pack(pady=8)

    tk.Button(
        reactivate_btn_frame,
        text="Reactivate User",
        font=FONT_BTN,
        bg="#4ee06e",
        fg=BTN_TEXT_COLOR,
        activebackground="#3ac454",
        command=reactivate_user
    ).pack()

    

    # Initial loads
    refresh_inventory()
    load_users()
    load_archived_users()
    load_all_transactions()



    # Add logout at bottom
    logout_frame = tk.Frame(admin, bg=BG_COLOR)
    logout_frame.pack(side="bottom", pady=10)
    tk.Button(
        logout_frame,
        text="Logout",
        font=FONT_BTN,
        bg="#e84c4c",
        fg="white",
        activebackground="#c9302c",
        command=lambda: (admin.destroy(), parent_window.deiconify() if parent_window else login_window())
    ).pack()


# ==================== staff panel ====================
def staff_panel(user, parent_window=None):
    if parent_window:
        parent_window.withdraw()

    staff = tk.Toplevel()
    staff.title(f"Staff Panel - {user['username']}")
    staff.geometry("1100x700")
    staff.configure(bg=BG_COLOR)
    staff.protocol("WM_DELETE_WINDOW", lambda: (parent_window.destroy()))

    tk.Label(staff, text=f"Staff Panel - Welcome {user['username']}", font=FONT_HEADER, fg=ACCENT_COLOR, bg=BG_COLOR).pack(pady=10)

    notebook = ttk.Notebook(staff)
    notebook.pack(fill="both", expand=True)

    # ==================== INVENTORY TAB ====================
    inventory_tab = tk.Frame(notebook, bg=BG_COLOR)
    notebook.add(inventory_tab, text="Manage Inventory")

    inv_tree = ttk.Treeview(inventory_tab, columns=("ID","Name","Category","Price","Stock"), show="headings", height=12)
    for col in ("ID","Name","Category","Price","Stock"):
        inv_tree.heading(col, text=col)
        inv_tree.column(col, anchor="center", width=120)
    inv_tree.pack(pady=10)

    currency_var = tk.StringVar(value="price_php")

    def refresh_inventory(_=None):
        inv_tree.delete(*inv_tree.get_children())
        conn = get_db()
        cur = conn.cursor()
        cur.execute(f"SELECT product_id,name,category,{currency_var.get()},stock FROM products WHERE is_active=1")
        for row in cur.fetchall():
            inv_tree.insert('', 'end', values=row)
        conn.close()

    refresh_inventory()

    tk.Button(inventory_tab, text="Refresh Inventory", font=FONT_BTN, bg=ACCENT_COLOR, fg=BTN_TEXT_COLOR,
          activebackground=BTN_HOVER, command=refresh_inventory).pack(pady=5)

    stock_frame = tk.Frame(inventory_tab, bg=BG_COLOR)
    stock_frame.pack(pady=6)
    tk.Label(stock_frame, text="Set New Stock:", font=FONT_LABEL, fg=FG_TEXT, bg=BG_COLOR).pack(side="left", padx=4)
    staff_qty = tk.IntVar(value=1)
    tk.Spinbox(stock_frame, from_=0, to=999, textvariable=staff_qty, width=6).pack(side="left", padx=4)

    def staff_update_stock():
        selected = inv_tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Choose a product!")
            return
        pid = inv_tree.item(selected[0])['values'][0]
        new_stock = staff_qty.get()
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.callproc('sp_update_stock', (pid, new_stock, user['user_id']))
            conn.commit()
            conn.close()
            messagebox.showinfo("Stock", "Stock updated!")
            refresh_inventory()
        except Exception as e:
            messagebox.showerror("Error", f"Could not update stock:\n{e}")

    tk.Button(stock_frame, text="Update Stock", font=FONT_BTN,
              bg=ACCENT_COLOR, fg=BTN_TEXT_COLOR,
              activebackground=BTN_HOVER,
              command=staff_update_stock).pack(side="left", padx=8)

    btn_frame = tk.Frame(inventory_tab, bg=BG_COLOR)
    btn_frame.pack(pady=8)
    tk.Button(btn_frame, text="Add Product", bg="#4ee06e", fg=BTN_TEXT_COLOR,
              font=FONT_BTN, activebackground="#3ac454",
              command=lambda: add_product(inv_tree, refresh_inventory)).grid(row=0, column=0, padx=8)
    tk.Button(btn_frame, text="Edit Product", bg="#f7d23a", fg=BTN_TEXT_COLOR,
              font=FONT_BTN, activebackground="#e6b92e",
              command=lambda: edit_product(inv_tree, refresh_inventory)).grid(row=0, column=1, padx=8)
    tk.Button(btn_frame, text="Delete Product", bg="#f7d23a", fg="#23272f",
              font=FONT_BTN, activebackground="#e84c4c",
              command=lambda: delete_product(inv_tree, refresh_inventory)).grid(row=0, column=2, padx=8)

    # ==================== PENDING ORDERS TAB ====================
    orders_tab = tk.Frame(notebook, bg=BG_COLOR)
    notebook.add(orders_tab, text="Pending Orders")

    tk.Label(orders_tab, text="Pending Orders", font=FONT_HEADER, fg=ACCENT_COLOR, bg=BG_COLOR).pack(pady=8)

    orders_tree = ttk.Treeview(orders_tab,
                               columns=("OrderID","Products","UserID","Date","Total","Status"),
                               show="headings", height=15)
    orders_tree.heading("OrderID", text="Order ID")
    orders_tree.heading("Products", text="Products")
    orders_tree.heading("UserID", text="User ID")
    orders_tree.heading("Date", text="Date")
    orders_tree.heading("Total", text="Total")
    orders_tree.heading("Status", text="Status")

    orders_tree.column("OrderID", width=80, anchor="center")
    orders_tree.column("Products", width=300, anchor="w")
    orders_tree.column("UserID", width=80, anchor="center")
    orders_tree.column("Date", width=150, anchor="center")
    orders_tree.column("Total", width=100, anchor="center")
    orders_tree.column("Status", width=100, anchor="center")
    orders_tree.pack(pady=10, fill="both", expand=True)

    def load_pending_orders():
        orders_tree.delete(*orders_tree.get_children())
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("""
                SELECT o.order_id,
                       GROUP_CONCAT(p.name SEPARATOR ', ') AS products,
                       o.user_id,
                       o.order_date,
                       o.total_php,
                       o.status
                FROM orders o
                JOIN order_items oi ON o.order_id = oi.order_id
                JOIN products p ON oi.product_id = p.product_id
                WHERE o.status='pending'
                GROUP BY o.order_id, o.user_id, o.order_date, o.total_php, o.status
                ORDER BY o.order_date DESC
            """)
            for row in cur.fetchall():
                orders_tree.insert('', 'end', values=row)
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load orders:\n{e}")

    def mark_as_on_the_way():
        selected = orders_tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Choose an order to update.")
            return
        order_id = orders_tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirm", f"Mark Order #{order_id} as On the Way?"):
            try:
                conn = get_db()
                cur = conn.cursor()
                cur.execute("UPDATE orders SET status='on_the_way' WHERE order_id=%s", (order_id,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Updated", f"Order #{order_id} is now On the Way.")
                load_pending_orders()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update order:\n{e}")

    # Buttons for pending orders
    pending_btn_frame = tk.Frame(orders_tab, bg=BG_COLOR)
    pending_btn_frame.pack(pady=8)

    tk.Button(
        pending_btn_frame,
        text="Mark as On The Way",
        font=FONT_BTN,
        bg=ACCENT_COLOR,
        fg=BTN_TEXT_COLOR,
        activebackground=BTN_HOVER,
        command=mark_as_on_the_way
    ).grid(row=0, column=0, padx=8)

    tk.Button(
        pending_btn_frame,
        text="Refresh",
        font=FONT_BTN,
        bg="#e0e1ea",
        fg="#23272f",
        activebackground="#cacbd1",
        command=load_pending_orders
    ).grid(row=0, column=1, padx=8)
    # ==================== ON THE WAY ORDERS TAB ====================
    ontheway_tab = tk.Frame(notebook, bg=BG_COLOR)
    notebook.add(ontheway_tab, text="On The Way Orders")

    tk.Label(ontheway_tab, text="On The Way Orders", font=FONT_HEADER, fg=ACCENT_COLOR, bg=BG_COLOR).pack(pady=8)

    ontheway_tree = ttk.Treeview(ontheway_tab,
                                 columns=("OrderID","Products","UserID","Date","Total","Status"),
                                 show="headings", height=15)
    for col in ("OrderID","Products","UserID","Date","Total","Status"):
        ontheway_tree.heading(col, text=col)
        ontheway_tree.column(col, anchor="center", width=120)
    ontheway_tree.column("Products", width=300, anchor="w")
    ontheway_tree.pack(pady=10, fill="both", expand=True)

    def load_on_the_way_orders():
        ontheway_tree.delete(*ontheway_tree.get_children())
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("""
                SELECT o.order_id, GROUP_CONCAT(p.name SEPARATOR ', ') AS products,
                       o.user_id, o.order_date, o.total_php, o.status
                FROM orders o
                JOIN order_items oi ON o.order_id = oi.order_id
                JOIN products p ON oi.product_id = p.product_id
                WHERE o.status='on_the_way'
                GROUP BY o.order_id, o.user_id, o.order_date, o.total_php, o.status
                ORDER BY o.order_date DESC
            """)
            for row in cur.fetchall():
                ontheway_tree.insert('', 'end', values=row)
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load On The Way orders:\n{e}")

    tk.Button(ontheway_tab, text="Refresh", font=FONT_BTN, bg="#e0e1ea", fg="#23272f",
              activebackground="#cacbd1", command=load_on_the_way_orders).pack(pady=10)

    # ==================== DELIVERED ORDERS TAB ====================
    delivered_tab = tk.Frame(notebook, bg=BG_COLOR)
    notebook.add(delivered_tab, text="Delivered Orders")

    tk.Label(delivered_tab, text="Delivered Orders", font=FONT_HEADER, fg=ACCENT_COLOR, bg=BG_COLOR).pack(pady=8)

    delivered_tree = ttk.Treeview(delivered_tab,
                                  columns=("OrderID","Products","UserID","Date","Total","Status"),
                                  show="headings", height=15)
    for col in ("OrderID","Products","UserID","Date","Total","Status"):
        delivered_tree.heading(col, text=col)
        delivered_tree.column(col, anchor="center", width=120)
    delivered_tree.pack(pady=10, fill="both", expand=True)

    def load_delivered_orders():
        delivered_tree.delete(*delivered_tree.get_children())
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("""
                SELECT o.order_id,
                       GROUP_CONCAT(p.name SEPARATOR ', ') AS products,
                       o.user_id,
                       o.order_date,
                       o.total_php,
                       o.status
                FROM orders o
                JOIN order_items oi ON o.order_id = oi.order_id
                JOIN products p ON oi.product_id = p.product_id
                WHERE o.status='completed'
                GROUP BY o.order_id, o.user_id, o.order_date, o.total_php, o.status
                ORDER BY o.order_date DESC
            """)
            for row in cur.fetchall():
                delivered_tree.insert('', 'end', values=row)
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load delivered orders:\n{e}")

    tk.Button(delivered_tab, text="Refresh", font=FONT_BTN, bg="#e0e1ea", fg="#23272f",
              activebackground="#cacbd1", command=load_delivered_orders).pack(pady=10)

    # Initial loads
    load_pending_orders()
    load_on_the_way_orders()
    load_delivered_orders()

    # Back button
    tk.Button(staff, text="Logout", font=FONT_BTN, bg="#e84c4c", fg="white",
              activebackground="#c9302c",
              command=lambda: (staff.destroy(), parent_window.deiconify() if parent_window else login_window())).pack(pady=10)


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

        try:
            conn = get_db()
            cur = conn.cursor(dictionary=True)
            # Fetch currency rates
            cur.execute("SELECT currency_code, exchange_rate_to_usd FROM currencies")
            rates = cur.fetchall()
            conn.close()

            # Default fallback values
            usd_rate = 58.0
            krw_rate = 23.6

            # Parse rates from table
            for r in rates:
                if r['currency_code'] == 'USD':
                    usd_rate = float(r['exchange_rate_to_usd'])
                elif r['currency_code'] == 'KRW':
                    # 1 PHP to KRW = (1 / USD rate) * (KRW/USD)
                    # OR you can store a direct PHP->KRW in the table if you prefer
                    # For now assume exchange_rate_to_usd is also valid for KRW
                    # (Adjust logic if your table stores differently)
                    krw_rate = 23.6
        except Exception as e:
            messagebox.showwarning("Currency Warning", f"Could not load currency rates. Using default.\n{e}")

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

def generate_sales_report(startdate, enddate):
    if startdate > enddate:
        messagebox.showerror("Error", "Start date must come before end date!")
        return
    try:
        conn = get_db()
        cur = conn.cursor()
        # Call the procedure (inserts into sales_reports)
        cur.callproc('sp_generate_sales_report', (startdate, enddate))
        conn.commit()

        # Fetch rows from sales_reports for this date range
        cur.execute("""
            SELECT o.order_id, u.username, o.order_date, o.total_php, o.status
            FROM orders o
            JOIN users u ON o.user_id = u.user_id
            WHERE o.order_date BETWEEN %s AND %s
            ORDER BY o.order_date DESC
        """, (startdate, enddate))
        rows = cur.fetchall()


        #  Create a new popup window
        report_win = tk.Toplevel()
        report_win.title("Sales Report")
        report_win.geometry("800x400")
        report_win.configure(bg=BG_COLOR)

        tk.Label(report_win, text=f"Sales Report ({startdate} to {enddate})",
                 font=FONT_HEADER, fg=ACCENT_COLOR, bg=BG_COLOR).pack(pady=10)

        #  Create a Treeview to display rows
        tree = ttk.Treeview(
            report_win,
            columns=("OrderID", "Username", "Date", "Total", "Status", "Generated"),
            show="headings",
            height=15
        )

        for col in ("OrderID", "Username", "Date", "Total", "Status", "Generated"):
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=120)
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        #  Insert rows into the Treeview
        for row in rows:
            tree.insert("", "end", values=row)

    except Exception as e:
        messagebox.showerror("Error", f"Sales report failed:\n{e}")

# ---- RUN LOGIN ----
if __name__ == "__main__":
    login_window()
