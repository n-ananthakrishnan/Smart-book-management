from flask import Flask, request, jsonify, render_template
import sqlite3
from pyzbar.pyzbar import decode
import cv2
import numpy as np

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan_barcode():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        barcodes = decode(frame)
        for barcode in barcodes:
            barcode_data = barcode.data.decode('utf-8')
            cap.release()
            cv2.destroyAllWindows()
            return jsonify(check_book_placement(barcode_data))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    return jsonify({'message': 'No barcode detected'})

def check_book_placement(barcode_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT title, rack_no, genre FROM books WHERE barcode = ?', (barcode_data,))
    book = cursor.fetchone()
    conn.close()
    if book:
        return {'title': book[0], 'rack_no': book[1], 'genre': book[2]}
    return {'message': 'Book not found'}

@app.route('/books', methods=['GET'])
def list_books():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT title, rack_no FROM books')
    books = cursor.fetchall()
    conn.close()
    return jsonify([{'title': book[0], 'rack_no': book[1]} for book in books])

@app.route('/add_book', methods=['POST'])
def add_book():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO books (title, barcode, rack_no, genre) VALUES (?, ?, ?, ?)',
                   (data['title'], data['barcode'], data['rack_no'], data['genre']))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Book added successfully'})

if __name__ == '__main__':
    app.run(debug=True)
