KeyKart Project Setup Instructions

1. Make sure you have Python 3.8 or newer installed on your computer.

2. Install the required Python dependency:
   pip install mysql-connector-python
   pip install pillow


3. Download and install MySQL if you haven’t yet. (You can use MySQL Workbench for a GUI, or use the command line.)

4. Open MySQL Workbench (or your preferred MySQL client) and **run the full contents of keykart.sql**.
   This will create the database, tables, triggers, stored procedures, and demo data.

5. Open the file keykart.py in your code editor (VS Code, PyCharm, etc).

6. In keykart.py, look for the get\_db() function at the top, and set your MySQL username and password.
   For example:
   def get\_db():
   return mysql.connector.connect(
   host="localhost",
   user="root",            # or your MySQL username
   password="yourpassword",# your MySQL password
   database="keykart"
   )

7. Save your changes.

8. Open a terminal or command prompt, navigate to the folder with keykart.py, and run:
   python keykart.py

9. Log in using the demo accounts:

   * Admin: admin / admin123
   * Staff: staff1 / staffpass
   * Customer: gamer1 / gamerpass

10. If you get any errors about missing modules, re-run:
    pip install mysql-connector-python

11. That’s it! The app should now work and you can log in, browse products, manage inventory, place orders, and more.

For any issues, double-check your MySQL credentials and make sure the database was created successfully by running the keykart.sql file.
