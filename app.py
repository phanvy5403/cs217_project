from flask import Flask, render_template, request, jsonify
import mysql.connector

app = Flask(__name__)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Phanvylqd@112',
    'database': 'luatgiaothong',
    'charset': 'utf8mb4'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def add_law():
    rule = request.form['rule']
    penalty = request.form['penalty']
    vehicle = request.form['vehicle']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO laws (rule, penalty, vehicle) VALUES (%s, %s, %s)",
        (rule, penalty, vehicle)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Luật được thêm thành công"})

@app.route('/search', methods=['GET'])
def search():
    # Get query parameters
    query = request.args.get('query', '').strip().lower()  
    vehicle = request.args.get('vehicle', '').strip().lower()
    penalty = request.args.get('penalty', '').strip().lower()

    # Establish database connection
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Construct base SQL query
    sql_query = """
        SELECT 
            loivipham.NoiDung AS LoiViPham,
            hinhphat.NoiDung AS HinhPhat,
            phuongtien.TenPhuongTien,
            chitietloi.NoiDung AS ChiTietLoi,
            luat.DieuKhoan,
            luat.NgayApDung
        FROM 
            luat
        JOIN 
            loivipham ON loivipham.LoiViPhamID = luat.LoiViPhamID
        JOIN 
            hinhphat ON hinhphat.HinhPhatID = luat.HinhPhatID
        JOIN 
            phuongtien ON phuongtien.PhuongTienID = luat.PhuongTienID
        JOIN 
            chitietloi ON chitietloi.ChiTietLoiID = luat.ChiTietLoiID
        WHERE 
            LOWER(loivipham.NoiDung) LIKE %s COLLATE utf8mb4_unicode_ci
    """

    params = [f"%{query}%"]

    if vehicle:
        sql_query += " AND LOWER(phuongtien.TenPhuongTien) = %s"
        params.append(vehicle)

    if penalty:
        sql_query += " AND LOWER(hinhphat.NoiDung) LIKE %s COLLATE utf8mb4_unicode_ci"
        params.append(f"%{penalty}%")

    # Execute the SQL query
    cursor.execute(sql_query, params)
    laws = cursor.fetchall()

    # Close database connection
    conn.close()

    # Return results as JSON
    return jsonify(laws)


if __name__ == '__main__':
    app.run(debug=True)
