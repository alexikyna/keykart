import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import mysql.connector

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
            cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (uname, pword))
            user = cur.fetchone()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not connect to MySQL.\n\n{e}")
            return
        if user:
            root.destroy()
            if user['role'] in ['admin', 'staff']:
                admin_panel(user)
            else:
                shop_window(user)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    root = tk.Tk()
    root.title("KeyKart | Login")
    root.geometry("400x360")
    root.configure(bg=BG_COLOR)
    root.resizable(False, False)

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
def shop_window(user):
    shop = tk.Tk()
    shop.title(f"KeyKart Shop - {user['username']}")
    shop.geometry("700x480")
    shop.configure(bg=BG_COLOR)

    tk.Label(shop, text=f"Welcome, {user['username']}!", font=FONT_HEADER, fg=ACCENT_COLOR, bg=BG_COLOR).pack(pady=(15, 5))
    tk.Label(shop, text="Product Catalog", font=FONT_LABEL, fg=FG_TEXT, bg=BG_COLOR).pack()

    tree = ttk.Treeview(shop, columns=("ID", "Name", "Category", "Price", "Stock"), show="headings", height=10)
    for col in ("ID", "Name", "Category", "Price", "Stock"):
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=120)
    tree.pack(pady=10)

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

    cart = []

    def refresh_products():
        for row in tree.get_children():
            tree.delete(row)
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT product_id, name, category, price_php, stock FROM products WHERE is_active=1")

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
        order_id = tree.item(selected[0])['values'][0]
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
def admin_panel(user):

    admin = tk.Tk()
    admin.title(f"Admin Panel - {user['username']}")
    admin.geometry("720x480")
    admin.configure(bg=BG_COLOR)

    tk.Label(admin, text="Admin Panel", font=FONT_HEADER, fg=ACCENT_COLOR, bg=BG_COLOR).pack(pady=20)

    tk.Button(admin, text="Manage Product Inventory", font=FONT_BTN, width=30, bg="#4ee06e", fg=BTN_TEXT_COLOR,
              activebackground="#3ac454", command=lambda: open_inventory_view(admin)).pack(pady=10)

    tk.Button(admin, text="Manage User Roles", font=FONT_BTN, width=30, bg="#3da6f0", fg="white",
              activebackground="#2b8ad4", command=open_user_roles_window).pack(pady=10)

    admin.mainloop()

    
def open_inventory_view(root_window):
    inventory_win = tk.Toplevel(root_window)
    inventory_win.title("Product Inventory")
    inventory_win.geometry("720x480")
    inventory_win.configure(bg=BG_COLOR)

    tk.Label(inventory_win, text="Product Inventory", font=FONT_HEADER, fg=ACCENT_COLOR, bg=BG_COLOR).pack(pady=10)

    tree = ttk.Treeview(inventory_win, columns=("ID", "Name", "Category", "Price", "Stock"), show="headings", height=12)
    for col in ("ID", "Name", "Category", "Price", "Stock"):
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=120)
    tree.pack(pady=8)

    btn_frame = tk.Frame(inventory_win, bg=BG_COLOR)
    btn_frame.pack(pady=8)

    tk.Button(btn_frame, text="Add Product", bg="#4ee06e", fg=BTN_TEXT_COLOR, font=FONT_BTN,
              activebackground="#3ac454", command=lambda: add_product(tree, refresh)).grid(row=0, column=0, padx=8)
    tk.Button(btn_frame, text="Edit Product", bg="#f7d23a", fg=BTN_TEXT_COLOR, font=FONT_BTN,
              activebackground="#e6b92e", command=lambda: edit_product(tree, refresh)).grid(row=0, column=1, padx=8)
    tk.Button(btn_frame, text="Delete Product", bg="#f7d23a", fg="#23272f", font=FONT_BTN,
              activebackground="#e84c4c", command=lambda: delete_product(tree, refresh)).grid(row=0, column=2, padx=8)

    # Stock update
    stock_frame = tk.Frame(inventory_win, bg=BG_COLOR)
    stock_frame.pack(pady=6)
    tk.Label(stock_frame, text="Set New Stock:", font=FONT_LABEL, fg=FG_TEXT, bg=BG_COLOR).pack(side="left", padx=4)
    simple_qty = tk.IntVar(value=1)
    tk.Spinbox(stock_frame, from_=0, to=999, textvariable=simple_qty, width=6).pack(side="left", padx=4)
    tk.Button(stock_frame, text="Update Stock", font=FONT_BTN, bg=ACCENT_COLOR, fg=BTN_TEXT_COLOR,
              activebackground=BTN_HOVER, command=lambda: update_stock(tree, simple_qty, None, refresh)).pack(side="left", padx=8)

    tk.Button(inventory_win, text="Refresh", font=FONT_BTN, bg="#e0e1ea", fg="#23272f",
              activebackground="#cacbd1", command=lambda: refresh(tree)).pack(pady=6)

    def refresh(tree):
        for row in tree.get_children():
            tree.delete(row)
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT product_id, name, category, price_php, stock FROM products WHERE is_active=1")
        for row in cur.fetchall():
            tree.insert('', 'end', values=row)
        conn.close()

    refresh(tree)

    admin.mainloop()

def open_user_roles_window():
    win = tk.Toplevel()
    win.title("Manage User Roles")
    win.geometry("600x400")
    win.configure(bg=BG_COLOR)

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

    load_users()


# ---------------- Admin Helper Functions ----------------
def add_product(tree, refresh):
    win = tk.Toplevel()
    win.title("Add Product")
    win.geometry("420x420")
    fields = ["Name", "Category", "Price PHP", "Price USD", "Price KRW", "Stock", "Description"]
    vars = [tk.StringVar() for _ in fields]
    categories = ['game_key', 'in_game_currency', 'merch']

    for i, label in enumerate(fields):
        tk.Label(win, text=label).grid(row=i, column=0, sticky='e', pady=5)
        if label == "Category":
            cb = ttk.Combobox(win, textvariable=vars[i], values=categories, state="readonly")
            cb.grid(row=i, column=1, pady=5)
        else:
            tk.Entry(win, textvariable=vars[i]).grid(row=i, column=1, pady=5)

    def save():
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""INSERT INTO products 
            (name, category, price_php, price_usd, price_krw, stock, description)
            VALUES (%s,%s,%s,%s,%s,%s,%s)""",
            [v.get() for v in vars])
        conn.commit()
        conn.close()
        win.destroy()
        refresh(tree)

    tk.Button(win, text="Save", bg="#4ee06e", fg=BTN_TEXT_COLOR, command=save).grid(row=len(fields), column=1, pady=14)

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
