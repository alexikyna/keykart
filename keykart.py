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
from PIL import Image, ImageTk
import urllib.request, io
import os
import uuid

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
        password="Password123",
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

    style = ttk.Style()
    style.theme_use('default')
    style.configure("TNotebook.Tab", padding=[20, 8])

    tk.Label(shop, text=f"Welcome, {user['username']}!", font=FONT_HEADER, fg=ACCENT_COLOR, bg=BG_COLOR).pack(pady=5)

    # --- Currency selector (shared) ---
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT currency_code FROM currencies")
    currency_codes = [row[0] for row in cur.fetchall()]
    conn.close()

    if not currency_codes:
        currency_codes = ["PHP"]  # fallback

    currency_var = tk.StringVar(value=currency_codes[0])

    currency_frame = tk.Frame(shop, bg=BG_COLOR)
    currency_frame.pack(pady=4)
    tk.Label(currency_frame, text="Currency:", font=FONT_LABEL, fg=FG_TEXT, bg=BG_COLOR).pack(side="left", padx=5)
    currency_cb = ttk.Combobox(currency_frame, textvariable=currency_var,
                            values=currency_codes, state="readonly")
    currency_cb.pack(side="left", padx=5)

    def on_currency_change(*args):
        tree.heading("Price", text=f"Price ({currency_var.get()})")
        orders_tree.heading("Total", text=f"Total ({currency_var.get()})")
        refresh_products()
        update_cart_prices()
        load_orders()

    currency_var.trace_add("write", on_currency_change)


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

    # inside shop_window (AFTER you create `tree`):
    def show_product_popup_customer(event):
        selected = tree.selection()
        if not selected:
            return
        pid = tree.item(selected[0])['values'][0]

        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT name, category, description, base_price_php, stock, image_url FROM products WHERE product_id=%s", (pid,))
            product = cur.fetchone()
            conn.close()
        except Exception as e:
            messagebox.showerror("DB Error", f"Failed to fetch product:\n{e}")
            return

        if not product:
            return

        name, category, desc, base_price_php, stock, image_url = product

        # fetch currencies
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT currency_code, symbol, exchange_rate_to_php FROM currencies")
            currencies = cur.fetchall()
            conn.close()
        except:
            currencies = [("PHP","₱",1.0)]

        popup = tk.Toplevel(shop)
        popup.title(name)
        popup.geometry("400x500")
        popup.configure(bg=BG_COLOR)

        tk.Label(popup, text=name, font=FONT_HEADER, fg=ACCENT_COLOR, bg=BG_COLOR).pack(pady=10)
        tk.Label(popup, text=f"Category: {category}", font=FONT_LABEL, fg=FG_TEXT, bg=BG_COLOR).pack(pady=2)
        tk.Label(popup, text=f"Description: {desc}", font=FONT_LABEL, fg=FG_TEXT, bg=BG_COLOR, wraplength=380, justify="left").pack(pady=2)

        # dynamic currencies
        for code, symbol, rate in currencies:
            converted = float(base_price_php) * float(rate)
            tk.Label(popup, text=f"Price ({code}): {symbol}{converted:.2f}", font=FONT_LABEL, fg=FG_TEXT, bg=BG_COLOR).pack(pady=2)

        tk.Label(popup, text=f"Stock: {stock}", font=FONT_LABEL, fg=FG_TEXT, bg=BG_COLOR).pack(pady=2)

        img_label = tk.Label(popup, bg=BG_COLOR)
        img_label.pack(pady=10)

        try:
            if image_url:
                if image_url.startswith("http"):
                    with urllib.request.urlopen(image_url) as u:
                        raw = u.read()
                    im = Image.open(io.BytesIO(raw))
                else:
                    if not os.path.isabs(image_url):
                        image_url = os.path.join(os.getcwd(), image_url)
                    im = Image.open(image_url)
                im = im.resize((150,150))
                photo = ImageTk.PhotoImage(im)
                img_label.config(image=photo)
                img_label.image = photo
            else:
                img_label.config(text="No image available", fg="white")
        except Exception as e:
            img_label.config(text="Error loading image", fg="red")

    # ✅ bind AFTER defining function
    tree.bind("<Double-1>", show_product_popup_customer)



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
        # fetch all products
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT product_id,name,category,base_price_php,stock FROM products WHERE is_active=1")
        products = cur.fetchall()
        conn.close()

        # get selected currency's rate
        selected_currency = currency_var.get()
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT exchange_rate_to_php FROM currencies WHERE currency_code=%s", (selected_currency,))
        row = cur.fetchone()
        conn.close()
        rate = float(row['exchange_rate_to_php']) if row else 1.0

        # insert rows with converted price
        for p in products:
            converted = float(p['base_price_php']) * rate
            tree.insert('', 'end', values=(p['product_id'], p['name'], p['category'], f"{converted:.2f}", p['stock']))


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
            stock = int(stock_str)
        except ValueError:
            messagebox.showerror("Data Error", "Invalid stock value.")
            return

        qty = qty_var.get()
        if qty > stock:
            messagebox.showwarning("Stock", "Not enough stock!")
            return

        # price will be recalculated later in update_cart_prices
        cart.append((pid, name, qty, 0, cat))
        update_cart_prices()
        messagebox.showinfo("Added", f"Added {qty} of {name} to cart.")

    def checkout(user, payment_method="Cash"):
        if not cart:
            messagebox.showwarning("Cart", "Cart is empty!")
            return
        try:
            conn = get_db()
            cur = conn.cursor()

            # ✅ Place each item in cart
            for item in cart:
                cur.callproc('sp_place_order', (user['user_id'], item[0], item[2]))
                cur.execute("SELECT LAST_INSERT_ID()")
                order_id = cur.fetchone()[0]
                # ❌ Removed direct status update
                # Orders (including game_key/currency) will remain pending
                # until staff/admin delivers a key or manually updates

            # ✅ Log payment in transaction_log
            cur.execute("""
                SELECT order_id, total_php 
                FROM orders 
                WHERE user_id=%s 
                ORDER BY order_date DESC 
                LIMIT %s
            """, (user['user_id'], len(cart)))
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
            messagebox.showinfo("Order", "Order placed! A staff/admin will deliver digital keys soon.")
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

        # 1. Fetch orders in PHP
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT o.order_id,
                GROUP_CONCAT(p.name SEPARATOR ', ') AS products,
                o.order_date,
                SUM(oi.qty * p.base_price_php) AS total_php,
                o.status
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN products p ON oi.product_id = p.product_id
            WHERE o.user_id=%s
            GROUP BY o.order_id, o.order_date, o.status
            ORDER BY o.order_date DESC
        """, (user['user_id'],))
        rows = cur.fetchall()
        conn.close()

        # 2. Get selected currency’s exchange rate
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT exchange_rate_to_php FROM currencies WHERE currency_code=%s", (currency_var.get(),))
        row = cur.fetchone()
        conn.close()
        rate = float(row['exchange_rate_to_php']) if row else 1.0

        # 3. Insert converted totals
        for r in rows:
            # r should have exactly 5 values in this order:
            order_id = r[0]
            products = r[1]
            order_date = r[2]
            total_php = r[3]
            status = r[4]
            converted_total = float(total_php) * rate if total_php is not None else 0.0
            orders_tree.insert('', 'end', values=(order_id, products, order_date, f"{converted_total:.2f}", status))


        # get currency rate
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT exchange_rate_to_php FROM currencies WHERE currency_code=%s", (currency_var.get(),))
        row = cur.fetchone()
        conn.close()
        rate = float(row['exchange_rate_to_php']) if row else 1.0


    def update_cart_prices():
        if not cart:
            cart_tree.delete(*cart_tree.get_children())
            cart_total_label.config(text="Total: 0.00")
            return

        # get currency rate
        selected_currency = currency_var.get()
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT exchange_rate_to_php FROM currencies WHERE currency_code=%s", (selected_currency,))
        row = cur.fetchone()
        conn.close()
        rate = float(row['exchange_rate_to_php']) if row else 1.0

        cart_tree.delete(*cart_tree.get_children())
        total = 0.0
        for item in cart:
            pid, pname, qty, _, cat = item
            # get base price
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT base_price_php FROM products WHERE product_id=%s", (pid,))
            base_price = cur.fetchone()[0]
            conn.close()

            converted_price = float(base_price) * rate
            subtotal = converted_price * qty
            total += subtotal
            cart_tree.insert("", "end", values=(pname, qty, f"{converted_price:.2f}", f"{subtotal:.2f}"))

        cart_total_label.config(text=f"Total: {total:.2f}")


    def update_currency(*args):
        # Update headings dynamically based on selected currency
        selected = currency_var.get()  # e.g. "PHP", "USD", "KRW"
        tree.heading("Price", text=f"Price ({selected})")
        orders_tree.heading("Total", text=f"Total ({selected})")

        # Refresh all data with the new currency rate
        refresh_products()
        load_orders()
        update_cart_prices()

    # Bind the trace
    currency_var.trace_add("write", update_currency)



    # =============== Tab 4: Delivered Game Keys ===============
    keys_tab = tk.Frame(notebook, bg=BG_COLOR)
    notebook.add(keys_tab, text="Game Keys")

    keys_tree = ttk.Treeview(keys_tab,
                            columns=("OrderID", "Product", "Key", "DeliveredAt"),
                            show="headings", height=12)
    for col, width in zip(("OrderID", "Product", "Key", "DeliveredAt"), (100, 200, 250, 150)):
        keys_tree.heading(col, text=col)
        keys_tree.column(col, anchor="center", width=width)
    keys_tree.column("Product", anchor="w", width=200)
    keys_tree.pack(pady=10, fill="both", expand=True)

    def load_game_keys():
        keys_tree.delete(*keys_tree.get_children())
        try:
            conn = get_db()
            cur = conn.cursor()
            # ✅ join orders, order_items, products, key_deliveries
            cur.execute("""
                SELECT o.order_id, p.name, k.game_key, k.delivered_at
                FROM key_deliveries k
                JOIN order_items oi ON k.order_item_id = oi.order_item_id
                JOIN products p ON oi.product_id = p.product_id
                JOIN orders o ON oi.order_id = o.order_id
                WHERE o.user_id = %s
                ORDER BY k.delivered_at DESC
            """, (user['user_id'],))
            for row in cur.fetchall():
                keys_tree.insert('', 'end', values=row)
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load game keys:\n{e}")

    # Add a refresh button
    tk.Button(keys_tab, text="Refresh", font=FONT_BTN, bg=ACCENT_COLOR, fg=BTN_TEXT_COLOR,
            activebackground=BTN_HOVER, command=load_game_keys).pack(pady=6)


    # Initial load
    refresh_products()
    load_orders()
    load_game_keys()


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

    # --- Notebook setup ---
    container = tk.Frame(admin, bg=BG_COLOR)
    container.pack(fill="both", expand=True)

    style = ttk.Style()
    style.theme_use('default')
    style.configure("TNotebook.Tab", padding=[40, 10])  # center tabs

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

    # Currency dropdown
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT currency_code FROM currencies")
    db_currencies = [row[0] for row in cur.fetchall()]
    conn.close()
    if not db_currencies:
        db_currencies = ["PHP"]
    currency_var = tk.StringVar(value=db_currencies[0])

    currency_frame = tk.Frame(inventory_tab, bg=BG_COLOR)
    currency_frame.pack()
    tk.Label(currency_frame, text="Currency:", font=FONT_LABEL, fg=FG_TEXT, bg=BG_COLOR).pack(side="left", padx=5)
    currency_cb = ttk.Combobox(currency_frame, textvariable=currency_var,
                               values=db_currencies, state="readonly")
    currency_cb.pack(side="left", padx=5)

    # Refresh inventory
    def refresh_inventory():
        inv_tree.delete(*inv_tree.get_children())
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT product_id,name,category,base_price_php,stock FROM products WHERE is_active=1")
        products = cur.fetchall()
        conn.close()

        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT exchange_rate_to_php FROM currencies WHERE currency_code=%s", (currency_var.get(),))
        row = cur.fetchone()
        conn.close()
        rate = float(row['exchange_rate_to_php']) if row else 1.0

        for p in products:
            converted = float(p['base_price_php']) * rate
            inv_tree.insert('', 'end', values=(p['product_id'], p['name'], p['category'],
                                               f"{converted:.2f}", p['stock']))

    def show_product_popup(event):
        sel = inv_tree.selection()
        if not sel:
            return
        pid = inv_tree.item(sel[0])['values'][0]
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT name, category, description, base_price_php, stock, image_url FROM products WHERE product_id=%s", (pid,))
            result = cur.fetchone()
            conn.close()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
            return
        if not result:
            return
        name, category, desc, base_price_php, stock, image_url = result

        # convert price
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT exchange_rate_to_php FROM currencies WHERE currency_code=%s", (currency_var.get(),))
        row = cur.fetchone()
        conn.close()
        rate = float(row['exchange_rate_to_php']) if row else 1.0
        converted_price = float(base_price_php) * rate

        popup = tk.Toplevel(inventory_tab)
        popup.title(name)
        popup.geometry("400x500")
        popup.configure(bg=BG_COLOR)
        tk.Label(popup, text=name, font=FONT_HEADER, fg=ACCENT_COLOR, bg=BG_COLOR).pack(pady=10)
        tk.Label(popup, text=f"Category: {category}", font=FONT_LABEL, fg=FG_TEXT, bg=BG_COLOR).pack()
        tk.Label(popup, text=f"Description: {desc}", font=FONT_LABEL, fg=FG_TEXT, bg=BG_COLOR, wraplength=380).pack()
        tk.Label(popup, text=f"Price ({currency_var.get()}): {converted_price:.2f}",
                 font=FONT_LABEL, fg=FG_TEXT, bg=BG_COLOR).pack()
        tk.Label(popup, text=f"Stock: {stock}", font=FONT_LABEL, fg=FG_TEXT, bg=BG_COLOR).pack()
        img_label = tk.Label(popup, bg=BG_COLOR)
        img_label.pack(pady=10)
        try:
            if image_url:
                if image_url.startswith("http"):
                    with urllib.request.urlopen(image_url) as u:
                        raw = u.read()
                    im = Image.open(io.BytesIO(raw))
                else:
                    im = Image.open(image_url)
                im = im.resize((150, 150))
                photo = ImageTk.PhotoImage(im)
                img_label.config(image=photo)
                img_label.image = photo
            else:
                img_label.config(text="No image")
        except:
            img_label.config(text="Image load error", fg="red")

    inv_tree.bind("<Double-1>", show_product_popup)
    currency_var.trace_add("write", lambda *_: (inv_tree.heading("Price", text=f"Price ({currency_var.get()})"),
                                                refresh_inventory()))

    # stock update
    stock_frame = tk.Frame(inventory_tab, bg=BG_COLOR)
    stock_frame.pack(pady=6)
    tk.Label(stock_frame, text="Set New Stock:", font=FONT_LABEL, fg=FG_TEXT, bg=BG_COLOR).pack(side="left", padx=4)
    qty_var = tk.IntVar(value=1)
    tk.Spinbox(stock_frame, from_=0, to=999, textvariable=qty_var, width=6).pack(side="left", padx=4)
    tk.Button(stock_frame, text="Update Stock", font=FONT_BTN,
              bg=ACCENT_COLOR, fg=BTN_TEXT_COLOR, activebackground=BTN_HOVER,
              command=lambda: update_stock(inv_tree, qty_var, user, refresh_inventory)).pack(side="left", padx=8)

    inv_btn_frame = tk.Frame(inventory_tab, bg=BG_COLOR)
    inv_btn_frame.pack(pady=8)
    tk.Button(inv_btn_frame, text="Add Product", bg="#4ee06e", fg=BTN_TEXT_COLOR,
              font=FONT_BTN, command=lambda: add_product(inv_tree, refresh_inventory)).grid(row=0, column=0, padx=8)
    tk.Button(inv_btn_frame, text="Edit Product", bg="#f7d23a", fg=BTN_TEXT_COLOR,
              font=FONT_BTN, command=lambda: edit_product(inv_tree, refresh_inventory)).grid(row=0, column=1, padx=8)
    tk.Button(inv_btn_frame, text="Delete Product", bg="#f7d23a", fg="#23272f",
              font=FONT_BTN, command=lambda: delete_product(inv_tree, refresh_inventory)).grid(row=0, column=2, padx=8)

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

    tk.Button(
        sales_frame,
        text="Generate Report",
        font=FONT_BTN,
        bg=ACCENT_COLOR,
        fg=BTN_TEXT_COLOR,
        activebackground=BTN_HOVER,
        command=lambda: generate_sales_report(
            datetime.date(start_year.get(), start_month.get(), start_day.get()),
            datetime.date(end_year.get(), end_month.get(), end_day.get())
        )
    ).pack(side="left", padx=10)

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

    

  # Initial load
    refresh_inventory()
    load_all_transactions()
    load_users()
    load_archived_users()

    # logout
    logout_frame = tk.Frame(admin, bg=BG_COLOR)
    logout_frame.pack(side="bottom", pady=10)
    tk.Button(logout_frame, text="Logout", font=FONT_BTN, bg="#e84c4c",
              fg="white", command=lambda: (admin.destroy(),
                                           parent_window.deiconify() if parent_window else login_window())).pack()


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
    
    style = ttk.Style()
    style.theme_use('default')
    style.configure("TNotebook.Tab", padding=[40, 10])

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


        # --- Popup for product details in staff panel ---
    def show_product_popup_staff(event):
        selected = inv_tree.selection()
        if not selected:
            return
        pid = inv_tree.item(selected[0])['values'][0]
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT name, category, description, base_price_php, stock, image_url FROM products WHERE product_id=%s", (pid,))
            result = cur.fetchone()
            conn.close()
        except Exception as e:
            messagebox.showerror("DB Error", f"Failed to fetch product:\n{e}")
            return

        if not result:
            return

        # ✅ unpack only the 6 columns you selected
        name, category, desc, php, stock, image_url = result

        popup = tk.Toplevel(staff)
        popup.title(name)
        popup.geometry("400x500")
        popup.configure(bg=BG_COLOR)

        tk.Label(popup, text=name, font=FONT_HEADER, fg=ACCENT_COLOR, bg=BG_COLOR).pack(pady=10)
        tk.Label(popup, text=f"Category: {category}", font=FONT_LABEL, fg=FG_TEXT, bg=BG_COLOR).pack(pady=2)
        tk.Label(popup, text=f"Description: {desc}", font=FONT_LABEL, fg=FG_TEXT,
                bg=BG_COLOR, wraplength=380, justify="left").pack(pady=2)
        tk.Label(popup, text=f"Price (PHP): {php}", font=FONT_LABEL, fg=FG_TEXT, bg=BG_COLOR).pack(pady=2)
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

    inv_tree.bind("<Double-1>", show_product_popup_staff)


    currency_var = tk.StringVar(value="PHP")  # ✅ default to PHP (matches your DB currency_code)


    def refresh_inventory():
        inv_tree.delete(*inv_tree.get_children())

        # fetch products
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT product_id,name,category,base_price_php,stock FROM products WHERE is_active=1")
        products = cur.fetchall()
        conn.close()

        # get currency rate
        selected_currency = currency_var.get()
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT exchange_rate_to_php FROM currencies WHERE currency_code=%s", (selected_currency,))
        row = cur.fetchone()
        conn.close()
        rate = float(row['exchange_rate_to_php']) if row else 1.0

        for p in products:
            converted = float(p['base_price_php']) * rate
            inv_tree.insert('', 'end', values=(p['product_id'], p['name'], p['category'], f"{converted:.2f}", p['stock']))

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

        try:
            # ✅ Check the categories in this order
            conn = get_db()
            cur = conn.cursor()
            cur.execute("""
                SELECT DISTINCT category
                FROM order_items oi
                JOIN products p ON oi.product_id = p.product_id
                WHERE oi.order_id = %s
            """, (order_id,))
            categories = [row[0] for row in cur.fetchall()]
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Could not verify product category:\n{e}")
            return

        # ✅ If any item is NOT merch, block
        for c in categories:
            if c != 'merch':  # only merch is allowed
                messagebox.showinfo(
                    "Not Allowed",
                    f"Order #{order_id} contains a non‑merch item ({c}).\n"
                    "Only merchandise orders can be marked as On The Way."
                )
                return

        # ✅ All good, proceed
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

    def check_low_stock_alerts():
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT a.alert_id, p.name, a.remaining_stock
            FROM stock_alerts a
            JOIN products p ON a.product_id = p.product_id
            WHERE a.seen = 0
        """)
        alerts = cur.fetchall()
        for alert in alerts:
            messagebox.showwarning(
                "Low Stock Alert",
                f"⚠️ {alert['name']} is low on stock ({alert['remaining_stock']} left)!"
            )
            # mark as seen
            cur.execute("UPDATE stock_alerts SET seen=1 WHERE alert_id=%s", (alert['alert_id'],))
        conn.commit()
        conn.close()

    def poll_alerts():
        check_low_stock_alerts()
        staff.after(5000, poll_alerts)  # check every 5 seconds

    poll_alerts()  # start the loop


    def prompt_deliver_key():
        selected = orders_tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Please select an order first.")
            return

        order_id = orders_tree.item(selected[0])['values'][0]

        # Get the first order_item_id for this order
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT order_item_id FROM order_items WHERE order_id=%s LIMIT 1", (order_id,))
            result = cur.fetchone()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Could not fetch order item:\n{e}")
            return

        if not result:
            messagebox.showwarning("No Item", f"No order items found for Order #{order_id}")
            return

        order_item_id = result[0]

        # Auto‑generate a dummy key (replace with your logic if you have real keys)
        auto_key = str(uuid.uuid4()).upper()[:16]  # like 'ABC123...'

        # Deliver immediately
        deliver_game_key(order_item_id, auto_key)

    # In your pending_btn_frame (or wherever you want to put it):
    tk.Button(
        pending_btn_frame,
        text="Deliver Game Key",
        font=FONT_BTN,
        bg="#4ee06e",
        fg=BTN_TEXT_COLOR,
        activebackground="#3ac454",
        command=prompt_deliver_key
    ).grid(row=0, column=2, padx=8)


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
            filetypes=[
                ("PNG Images", "*.png"),
                ("JPEG Images", "*.jpg"),
                ("JPEG Images", "*.jpeg"),
                ("GIF Images", "*.gif")
            ]
        )

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

        # Optional: you can still do conversions for USD and KRW if you want,
        # but we will not store them in the database since those columns do not exist.
        try:
            conn = get_db()
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT currency_code, exchange_rate_to_php FROM currencies")
            rates = cur.fetchall()
            conn.close()

            php_to_usd = 0.0172   # fallback
            krw_to_usd = None

            for r in rates:
                if r['currency_code'] == 'PHP':
                    php_to_usd = float(r['exchange_rate_to_php'])
                elif r['currency_code'] == 'KRW':
                    krw_to_usd = float(r['exchange_rate_to_php'])

            # just for reference (not saved in DB)
            usd_price = round(php_price * php_to_usd, 2) if php_to_usd else 0
            krw_price = round((php_price * php_to_usd) / krw_to_usd, 0) if (php_to_usd and krw_to_usd) else 0

        except Exception as e:
            messagebox.showwarning("Currency Warning", f"Could not load currency rates. Using fallback.\n{e}")
            usd_price = round(php_price / 58.0, 2)
            krw_price = round(php_price * 23.6, 0)

        try:
            conn = get_db()
            cur = conn.cursor()
            # ✅ Fixed: match your actual table schema
            cur.execute("""INSERT INTO products
                (name, category, base_price_php, stock, description, image_url)
                VALUES (%s,%s,%s,%s,%s,%s)""",
                (
                    vars[0].get(),          # name
                    vars[1].get(),          # category
                    php_price,              # base_price_php
                    vars[3].get(),          # stock
                    vars[4].get(),          # description
                    image_path.get()        # image_url
                ))
            conn.commit()
            conn.close()
            messagebox.showinfo("Saved", "Product added successfully!")
            win.destroy()
            refresh()
        except Exception as e:
            messagebox.showerror("Error", f"Could not add product:\n{e}")

    tk.Button(win, text="Save", bg="#4ee06e", fg=BTN_TEXT_COLOR,
              command=save).grid(row=len(fields)+1, column=1, pady=14)

    
def edit_product(tree, refresh):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Select", "Choose a product!")
        return

    # Your tree currently has these columns: ID, Name, Category, Price, Stock
    values = tree.item(selected[0])['values']
    pid = values[0]
    name = values[1]
    cat = values[2]
    stock = values[4]  # ✅ index 4 because [ID, Name, Category, Price, Stock]

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
        refresh()


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
            refresh()
        except Exception as e:
            messagebox.showerror("Error", f"Could not archive product:\n{e}")

def deliver_game_key(order_item_id, game_key):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO key_deliveries (order_item_id, game_key) VALUES (%s, %s)",
            (order_item_id, game_key)
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", f"Game key delivered!\nOrder item #{order_item_id} is now marked completed.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to deliver key:\n{e}")


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

        # ✅ Call the stored procedure
        cur.callproc('sp_generate_sales_report', (startdate, enddate))

        # ✅ Fetch results returned by the stored procedure
        rows = []
        for result in cur.stored_results():
            rows = result.fetchall()  # rows now include generated_at

        # ✅ Create a popup window
        report_win = tk.Toplevel()
        report_win.title("Sales Report")
        report_win.geometry("800x400")
        report_win.configure(bg=BG_COLOR)

        tk.Label(
            report_win,
            text=f"Sales Report ({startdate} to {enddate})",
            font=FONT_HEADER,
            fg=ACCENT_COLOR,
            bg=BG_COLOR
        ).pack(pady=10)

        # ✅ Treeview with 6 columns, including Generated
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

        # ✅ Insert rows directly from procedure
        for row in rows:
            tree.insert("", "end", values=row)

        conn.close()

    except Exception as e:
        messagebox.showerror("Error", f"Sales report failed:\n{e}")


# ---- RUN LOGIN ----
if __name__ == "__main__":
    login_window()
