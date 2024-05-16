import sqlite3
import tkinter as tk
from io import BytesIO

from PIL import ImageGrab, ImageTk
from PIL.Image import Image
from PyQt5.QtGui import QPixmap

con = sqlite3.connect("HelperDatabase.db")
cur = con.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS treedata (
        id INTEGER PRIMARY KEY,
        name TEXT,
        exmp TEXT,
        descr TEXT,
        bphoto TEXT
    )
""")
con.commit()
def createTable(tablename):
    cur.execute(f"CREATE TABLE {tablename} (id INTEGER PRIMARY KEY, name TEXT, exmp TEXT,descr TEXT, bphoto TEXT )")
    con.commit()
def addFunctionInf(tablename,FunctionUse, FunExamp, FunDescription, FunPhoto):
    cur.execute(f"INSERT INTO {tablename} VALUES (NULL,?,?,?,?)", (FunctionUse, FunExamp, FunDescription, FunPhoto))
    con.commit()
def showData(table=''):
    cur.execute(f"SELECT * FROM {table}")
    rows = cur.fetchall()
    return rows
def return_image(id):
    # Get a list of all tables in the database
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cur.fetchall()

    for table in tables:
        table_name = table[0]
        # Check if the table has a 'bphoto' column
        cur.execute(f"PRAGMA table_info({table_name})")
        columns = cur.fetchall()
        column_names = [column[1] for column in columns]

        if 'bphoto' in column_names:
            # Search for the 'bphoto' column in the current table
            cur.execute(f"SELECT bphoto FROM {table_name} WHERE name = ?", (id,))
            img = cur.fetchone()
            if img:
                pixmap = QPixmap(600,600)
                pixmap.loadFromData(img[0])
                return pixmap
def showTables():
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    rows = cur.fetchall()
    return rows

def searchData(name):
    cur.execute(
        f"SELECT * FROM treedata WHERE FunctionDescription LIKE '%s'" % name)  ##################### '' LIKE '%s%'"% THE % solves value error
    rows = cur.fetchall()
    return rows
def deleteRec(tablename,name):
    cur.execute(f"DELETE FROM {tablename} WHERE name = '%s'"%name)
    con.commit()
def searchDataFromAllTables(search_term):
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    table_names = [row[0] for row in cur.fetchall()]
    results = []  # create an empty list to store the results

    # Loop through each table and execute a SELECT statement with a WHERE clause that uses the LIKE operator
    for table_name in table_names:
        cur.execute(
            f"SELECT * FROM {table_name} WHERE descr LIKE ?",
            ('%' + search_term + '%',)
        )
        rows = cur.fetchall()
        for row in rows:
            results.append(row)  # append each row to the results list
    return results
def delTable(tablename):
    cur.execute("DROP TABLE IF EXISTS " + tablename)
    con.commit()
def update_image(id, photo):
    with open(photo, 'rb') as f:
        data = f.read()
        cur.execute("UPDATE functionINF SET photo=(?) WHERE id=?", (data, id))
        con.commit()
def cropScreenshot(table='',mode='',image_path=''):
    if image_path:
        scrShot = Image.open(image_path)
    else:
        scrShot = ImageGrab.grab()
    topx, topy, botx, boty = 0, 0, 0, 0

    def get_mouse_posn(event):
        global topy, topx
        topx, topy = event.x, event.y

    def update_sel_rect(event):
        global topy, topx, botx, boty
        botx, boty = event.x, event.y
        canvas.coords(rect_id, topx, topy, botx, boty)  # Update selection rect.

    def finalImage(event):
        if mode == "database":
            popup = tk.Toplevel()
            var = tk.BooleanVar()
            fUse = tk.Entry(popup)
            fDes = tk.Entry(popup)
            ftext = tk.Text(popup, width=20, height=10)

            fUse.grid(row=1, column=1)
            fDes.grid(row=2, column=1)

            tk.Label(popup, text="Function Type").grid(row=1, column=0)
            tk.Label(popup, text="Function Description").grid(row=2, column=0)
            tk.Label(popup, text="Code").grid(row=5, column=0)
            ftext.grid(row=4, column=1)

            tk.Checkbutton(popup, variable=var, text="Bookmark").grid(row=0, column=1)
            tk.Button(popup, width=10, text='Add', command=lambda: finaloutput()).grid(row=3)
            popup.grid()

            def finaloutput():
                if mode == 'database':
                    imggg = scrShot.crop(canvas.coords(rect_id))  # canvas.cords returns the coordinates of the selected area
                    bytes_obj = BytesIO()
                    imggg.save(bytes_obj, 'PNG')
                    bytimg = bytes_obj.getvalue()
                    addFunctionInf(table,fUse.get(), fDes.get(), ftext.get('1.0', 'end'), bytimg,)
                    popup.destroy()
                    window.destroy()

        elif mode == 'cords':
            print(canvas.coords(rect_id), "\n")

    try:

        window = tk.Tk()
        img = ImageTk.PhotoImage(scrShot)
        canvas = tk.Canvas(window, width=img.width(), height=img.height(),
                           borderwidth=0, highlightthickness=0)
        canvas.pack(expand=True)
        canvas.img = img  # Keep reference in case this code is put into a function.
        canvas.create_image(0, 0, image=img, anchor=tk.NW)
        # Create selection rectangle (invisible since corner points are equal).
        rect_id = canvas.create_rectangle(topx, topy, topx, topy, dash=(2, 2), fill='', outline='white')

        canvas.bind('<Button-1>', get_mouse_posn)  # blind to mouse left click
        canvas.bind('<B1-Motion>', update_sel_rect)  # detects the motion of the mouse
        canvas.bind("<ButtonRelease-1>", finalImage)  # if left button is released
        window.mainloop()

    except:
        pass