import sqlite3

connection = sqlite3.connect('library.db')
cursor = connection.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS Books (
    BookID INTEGER PRIMARY KEY AUTOINCREMENT,
    Title TEXT,
    Author TEXT,
    ISBN TEXT,
    Status TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Users (
    UserID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT,
    Email TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Reservations (
    ReservationID INTEGER PRIMARY KEY AUTOINCREMENT,
    BookID INTEGER,
    UserID INTEGER,
    ReservationDate TEXT,
    FOREIGN KEY (BookID) REFERENCES Books(BookID),
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
)''')

connection.commit()

def add_book(title, author, isbn):
    cursor.execute("INSERT INTO Books (Title, Author, ISBN, Status) VALUES (?, ?, ?, 'Available')",
                   (title, author, isbn))
    connection.commit()
    print("Book added successfully!")

def find_book(book_id):
    cursor.execute("SELECT * FROM Books WHERE BookID = ?", (book_id,))
    book = cursor.fetchone()
    if book is None:
        print("Book not found!")
        return

    cursor.execute("SELECT * FROM Reservations WHERE BookID = ?", (book_id,))
    reservation = cursor.fetchone()

    if reservation is None:
        print("Book is available. No reservation.")
    else:
        user_id = reservation[2]
        cursor.execute("SELECT * FROM Users WHERE UserID = ?", (user_id,))
        user = cursor.fetchone()

        print("Book Details:")
        print("BookID:", book[0])
        print("Title:", book[1])
        print("Author:", book[2])
        print("ISBN:", book[3])
        print("Status:", book[4])
        print("Reserved by:")
        print("UserID:", user[0])
        print("Name:", user[1])
        print("Email:", user[2])

def find_reservation(text):
    found = False

    if text.startswith("LB"):
        cursor.execute("SELECT * FROM Books WHERE BookID = ?", (text,))
        book = cursor.fetchone()
        if book is not None:
            cursor.execute("SELECT * FROM Reservations WHERE BookID = ?", (book[0],))
            reservations = cursor.fetchall()
            print("Reservation status for BookID", book[0], "(", book[1], "):")
            for reservation in reservations:
                user_id = reservation[2]
                cursor.execute("SELECT * FROM Users WHERE UserID = ?", (user_id,))
                user = cursor.fetchone()
                print("- ReservationID:", reservation[0])
                print("  UserID:", user[0])
                print("  Name:", user[1])
                print("  Email:", user[2])
            found = True

    elif text.startswith("LU"):
        cursor.execute("SELECT * FROM Users WHERE UserID = ?", (text,))
        user = cursor.fetchone()
        if user is not None:
            cursor.execute("SELECT * FROM Reservations WHERE UserID = ?", (user[0],))
            reservations = cursor.fetchall()
            print("Reservation status for UserID", user[0], "(", user[1], "):")
            for reservation in reservations:
                cursor.execute("SELECT * FROM Books WHERE BookID = ?", (reservation[1],))
                book = cursor.fetchone()
                print("- ReservationID:", reservation[0])
                print("  BookID:", book[0])
                print("  Title:", book[1])
                print("  Author:", book[2])
                print("  ISBN:", book[3])
                print("  Status:", book[4])
            found = True

    elif text.startswith("LR"):
        cursor.execute("SELECT * FROM Reservations WHERE ReservationID = ?", (text,))
        reservation = cursor.fetchone()
        if reservation is not None:
            cursor.execute("SELECT * FROM Books WHERE BookID = ?", (reservation[1],))
            book = cursor.fetchone()
            cursor.execute("SELECT * FROM Users WHERE UserID = ?", (reservation[2],))
            user = cursor.fetchone()
            print("Reservation status for ReservationID", reservation[0], ":")
            print("BookID:", book[0])
            print("Title:", book[1])
            print("Author:", book[2])
            print("ISBN:", book[3])
            print("Status:", book[4])
            print("UserID:", user[0])
            print("Name:", user[1])
            print("Email:", user[2])
            found = True
    
    if not found:
        print("Book or reservation not found!")

def find_all_books():
    cursor.execute('''SELECT Books.BookID, Books.Title, Books.Author, Books.ISBN, Books.Status,
                      Users.UserID, Users.Name, Users.Email,
                      Reservations.ReservationID, Reservations.ReservationDate
                   FROM Books
                   LEFT JOIN Reservations ON Books.BookID = Reservations.BookID
                   LEFT JOIN Users ON Reservations.UserID = Users.UserID''')
    rows = cursor.fetchall()

    print("All Books in the Database:")
    for row in rows:
        print("BookID:", row[0])
        print("Title:", row[1])
        print("Author:", row[2])
        print("ISBN:", row[3])
        print("Status:", row[4])
        if row[5] is not None:
            print("Reserved by:")
            print("UserID:", row[5])
            print("Name:", row[6])
            print("Email:", row[7])
            print("ReservationID:", row[8])
            print("ReservationDate:", row[9])
        print()

def update_book(book_id, field, value):
    if field == 'Status':
        cursor.execute("UPDATE Books SET Status = ? WHERE BookID = ?", (value, book_id))
        cursor.execute("UPDATE Reservations SET ReservationDate = NULL WHERE BookID = ?", (book_id,))
        connection.commit()
        print("Book status updated successfully!")
    else:
        cursor.execute("UPDATE Books SET {} = ? WHERE BookID = ?".format(field), (value, book_id))
        connection.commit()
        print("Book details updated successfully!")

def delete_book(book_id):
    cursor.execute("SELECT * FROM Reservations WHERE BookID = ?", (book_id,))
    reservation = cursor.fetchone()
    if reservation is not None:
        cursor.execute("DELETE FROM Reservations WHERE BookID = ?", (book_id,))
    cursor.execute("DELETE FROM Books WHERE BookID = ?", (book_id,))
    connection.commit()
    print("Book deleted successfully!")

while True:
    print("\nLibrary Management System")
    print("1. Add a new book to the database")
    print("2. Find a book's details based on BookID")
    print("3. Find a book's reservation status")
    print("4. Find all books in the database")
    print("5. Modify/update book details based on BookID")
    print("6. Delete a book based on BookID")
    print("7. Exit")

    choice = input("Choose an option: ")

    if choice == "1":
        title = input("Enter the book's title: ")
        author = input("Enter the book's author: ")
        isbn = input("Enter the book's ISBN: ")
        add_book(title, author, isbn)

    elif choice == "2":
        book_id = input("Enter the BookID: ")
        find_book(book_id)

    elif choice == "3":
        text = input("Enter BookID, UserID, ReservationID, or Title: ")
        find_reservation(text)

    elif choice == "4":
        find_all_books()

    elif choice == "5":
        book_id = input("Enter the BookID: ")
        field = input("Enter the field to modify (Title, Author, ISBN, Status): ")
        value = input("Enter the new value: ")
        update_book(book_id, field, value)

    elif choice == "6":
        book_id = input("Enter the BookID: ")
        delete_book(book_id)

    elif choice == "7":
        print("Goodbye!")
        break

    else:
        print("Invalid choice. Please try again.")