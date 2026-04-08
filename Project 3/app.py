import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import hashlib


def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


def verify_user(username, pw):
    cur.execute("SELECT password_hash, role FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    if row and row[0] == hash_pw(pw):
        return True, row[1]
    return False, None


def add_user():
    u, p, r = u_name_enter.get().strip(), u_pass_enter.get().strip(), u_role_var.get()
    if not u or not p:
        return messagebox.showwarning("Input", "Enter username and password")
    try:
        cur.execute("INSERT INTO users VALUES (?, ?, ?)", (u, hash_pw(p), r))
        con.commit()
        messagebox.showinfo("Success", f"User '{u}' created as {r}'")
        u_name_enter.delete(0, tk.END)
        u_pass_enter.delete(0, tk.END)
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Username already exists")


def add_item():
    try:
        sku = i_sku.get().strip()
        desc = i_desc.get().strip()
        cost = float(i_cost.get())
        price = float(i_price.get())
        qty = int(i_price.get())

        if price < 0 or cost < 0 or qty < 0:
            raise ValueError

        cur.execute(
            "INSERT INTO inventory VALUES (?, ?, ?, ?, ?)",
            (sku, desc, cost, price, qty),
        )
        con.commit()
        refresh_inventory()
        for e in (i_sku, i_desc, i_cost, i_price, i_qty):
            e.delete(0, tk.END)
    except ValueError:
        messagebox.showerror("Input", "Invalid numbers or empty fields")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "SKU already exists")


def refresh_inventory():
    inv_tree.delete(*inv_tree.get_children())
    cur.execute(
        "SELECT sku, description, unit_cost, sale_price, qty_on_hand FROM inventory"
    )

    for row in cur.fetchall():
        sku, desc, cost, price, qty = row
        profit = round((price - cost) * qty, 2)
        inv_tree.insert(
            "",
            "end",
            values=(sku, desc, f"${cost:.2f}", f"${price:.2f}", qty, f"${profit:.2f}"),
        )


con = sqlite3.connect("register.db")
cur = con.cursor()
cur.execute("PRAGMA foreign_keys = ON;")

# Init db
cur.execute(
    """CREATE TABLE IF NOT EXISTS inventory (
    sku TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    unit_cost REAL NOT NULL,
    sale_price REAL NOT NULL,
    qty_on_hand INTEGER NOT NULL DEFAULT 0
);"""
)
cur.execute(
    """CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'cashier'
);"""
)
cur.execute(
    """CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    sku TEXT NOT NULL,
    qty INTEGER NOT NULL,
    subtotal REAL NOT NULL,
    tax REAL NOT NULL,
    total REAL NOT NULL,
    recorded_by TEXT NOT NULL,
    FOREIGN KEY(sku) REFERENCES inventory(sku),
    FOREIGN KEY(recorded_by) REFERENCES users(username)
);"""
)
con.commit()
cur.execute("SELECT COUNT(*) FROM inventory")
if cur.fetchone()[0] == 0:
    seeds = [
        ("1001", "Notebook", 1.50, 3.99, 50),
        ("1002", "Ballpoint Pen", 0.30, 1.25, 200),
        ("1003", "Stapler", 4.00, 8.99, 30),
        ("1004", "Paper Ream", 3.50, 7.49, 40),
        ("1005", "Highlighter", 0.40, 1.99, 150),
        ("1006", "Binder", 2.00, 5.99, 60),
        ("1007", "Scissors", 1.80, 4.49, 45),
        ("1008", "Tape Dispenser", 2.50, 6.99, 35),
        ("1009", "Desk Organizer", 6.00, 14.99, 20),
        ("1010", "Sticky Notes", 0.90, 2.49, 100),
    ]
    cur.executemany("INSERT INTO inventory VALUES (?, ?, ?, ?, ?)", seeds)
    con.commit()

cur.execute("SELECT COUNT(*) FROM users")
if cur.fetchone()[0] == 0:
    cur.execute(
        "INSERT INTO users VALUES (?, ?, ?)", ("admin", hash_pw("admin123"), "admin")
    )
    con.commit()


root = tk.Tk()
root.title("Cash Register")
root.geometry("750x550")

nav = tk.Frame(root)
nav.pack_forget()

admin_frame = tk.Frame(root)
cashier_frame = tk.Frame(root)

# Admin frame
ttk.Label(admin_frame, text="Admin Panel", font=("Arial", 16)).pack(pady=20)
u_frame = tk.Frame(admin_frame)
u_frame.pack(fill="x", padx=10, pady=5)

i_frame = tk.Frame(admin_frame)
i_frame.pack(fill="x", padx=10, pady=5)

ttk.Label(admin_frame, text="Current Inventory", font=("Arial", 10, "bold")).pack(
    anchor="w", padx=10, pady=(10, 0)
)
cols = ("sku", "desc", "cost", "price", "qty", "profit")
inv_tree = ttk.Treeview(admin_frame, columns=cols, show="headings")
inv_tree.pack(fill="both", expand=True, padx=10, pady=5)

for c, w in zip(cols, [60, 120, 60, 60, 50, 70]):
    inv_tree.heading(c, text=c.upper())
    inv_tree.column(c, width=w, anchor="center")

ttk.Label(i_frame, text="Add Item:", font=("Arial", 10, "bold")).pack(anchor="w")

i_sku = ttk.Entry(i_frame, width=8)
i_sku.pack(side="left", padx=2)
i_desc = ttk.Entry(i_frame, width=14)
i_desc.pack(side="left", padx=2)
i_cost = ttk.Entry(i_frame, width=6)
i_cost.pack(side="left", padx=2)
i_price = ttk.Entry(i_frame, width=6)
i_price.pack(side="left", padx=2)
i_qty = ttk.Entry(i_frame, width=5)
i_qty.pack(side="left", padx=2)
ttk.Button(i_frame, text="Add Item", command=add_item).pack(side="left", padx=5)


ttk.Label(u_frame, text="Create User:", font=("Arial", 10, "bold")).pack(anchor="w")
u_name_enter = ttk.Entry(u_frame, width=12)
u_name_enter.pack(side="left", padx=2)
u_pass_enter = ttk.Entry(u_frame, width=12, show="*")
u_pass_enter.pack(side="left", padx=2)
u_role_var = tk.StringVar(value="cashier")
u_role_cb = ttk.Combobox(
    u_frame,
    textvariable=u_role_var,
    values=["admin", "cashier"],
    width=9,
    state="readonly",
)
u_role_cb.pack(side="left", padx=2)
ttk.Button(u_frame, text="Add User", command=add_user).pack(side="left", padx=5)


# Cashier frame
ttk.Label(cashier_frame, text="Cashier Panel", font=("Arial", 16)).pack(pady=20)


current_user = None
current_role = None


def attempt_login():
    global current_user
    global current_role

    u = user_entry.get().strip()
    p = pass_entry.get().strip()

    if not u or not p:
        return messagebox.showwarning("Input", "Enter username and password")

    success, role = verify_user(u, p)
    if success:
        current_user = u
        current_role = role
        login_frame.pack_forget()
        nav.pack(fill="x", padx=10, pady=5)

        admin_frame.pack_forget()
        cashier_frame.pack_forget()

        if role == "admin":
            admin_frame.pack(fill="both", expand=True)
            refresh_inventory()
        else:
            cashier_frame.pack(fill="both", expand=True)
    else:
        messagebox.showerror("Login", "Invalid credentials")


login_frame = tk.Frame(root)
ttk.Label(login_frame, text="Cash Register Login", font=("Arial", 14)).pack(pady=10)
user_entry = ttk.Entry(login_frame, width=25)
user_entry.pack(pady=5)
user_entry.focus()
pass_entry = ttk.Entry(login_frame, width=25, show="*")
pass_entry.pack(pady=5)
ttk.Button(login_frame, text="Login", command=attempt_login).pack(pady=10)

login_frame.pack(fill="both", expand=True)


root.mainloop()
