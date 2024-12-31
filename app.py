from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Phanvylqd@112',
    'database': 'luatgiaothong',
    'charset': 'utf8mb4'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return User(user['id'], user['username'])
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            login_user(User(user['id'], user['username']))
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    return render_template('index.html')

@app.route('/add', methods=['POST'])
@login_required
def add_law():
    data = request.get_json()
    dieukhoan = data.get('DieuKhoan')
    hinhphat = data.get('HinhPhat')
    phuongtien = data.get('TenPhuongTien')
    loivipham = data.get('LoiViPham')
    chitietloi = data.get('ChiTietLoi')
    ngayapdung = data.get('NgayApDung')
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT PhuongTienID from PhuongTien WHERE TenPhuongTien = %s", (phuongtien,))
        phuongtien_id = cursor.fetchone()[0]

        cursor.execute("SELECT LoiViPhamID from LoiViPham WHERE LoiViPham.NoiDung = %s", (loivipham,))
        loivipham_id = cursor.fetchone()[0]

        if chitietloi:
            cursor.execute("SELECT ChiTietLoiID FROM ChiTietLoi WHERE NoiDung = %s", (chitietloi,))
            result = cursor.fetchone()
            if result:
                chitietloi_id = result[0]
            else:
                cursor.execute("INSERT INTO ChiTietLoi (NoiDung) VALUES (%s)", (chitietloi,))
                chitietloi_id = cursor.lastrowid
        else:
            chitietloi_id = None

        cursor.execute("INSERT INTO HinhPhat (NoiDung) VALUES (%s)", (hinhphat,))
        hinhphat_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO Luat (LoiViPhamID, PhuongTienID, ChiTietLoiID, HinhPhatID, DieuKhoan, NgayApDung)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (loivipham_id, phuongtien_id, chitietloi_id, hinhphat_id, dieukhoan, ngayapdung))
        
        conn.commit()
        # Return success response
        return jsonify({'success': True, 'message': 'Law added successfully!'})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
    finally:
        # Close the connection
        cursor.close()
        conn.close()

# API route to delete a law
@app.route('/delete/<int:law_id>', methods=['DELETE'])
@login_required
def delete_law(law_id):
    # Connect to the database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Delete query
    sql_delete = "DELETE FROM laws WHERE ID = %s"
    cursor.execute(sql_delete, (law_id,))
    conn.commit()

    # Close the connection
    cursor.close()
    conn.close()

    return jsonify({'message': 'Law deleted successfully!'})

# API route to update a law
@app.route('/update/<int:law_id>', methods=['PUT'])
@login_required
def update_law(law_id):
    data = request.get_json()
    hinh_phat = data.get('HinhPhat')
    ngay_ap_dung = data.get('NgayApDung')

    # Validate inputs
    if not hinh_phat or not ngay_ap_dung:
        return jsonify({'message': 'Hình phạt và Ngày Áp Dụng là bắt buộc!'}), 400

    # Connect to the database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    try:
        # Update query
        sql_update = """
            UPDATE luat
            SET HinhPhatID = (SELECT HinhPhatID FROM HinhPhat WHERE NoiDung = %s),
                NgayApDung = %s
            WHERE ID = %s
        """
        cursor.execute(sql_update, (hinh_phat, ngay_ap_dung, law_id))
        conn.commit()

        return jsonify({'message': 'Cập nhật luật thành công!'})
    except Exception as e:
        conn.rollback()
        return jsonify({'message': f'Lỗi: {str(e)}'}), 500
    finally:
        # Close the connection
        cursor.close()
        conn.close()

@app.route('/search', methods=['GET'])
@login_required
def search():
    # Get query parameters
    query = request.args.get('query', '').strip().lower()
    vehicle = request.args.get('vehicle', '').strip().lower()
    penalty = request.args.get('penalty', '').strip().lower()
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 2))  # Set default per_page to 2

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

    # Add pagination
    sql_query += " LIMIT %s OFFSET %s"
    params.extend([per_page, (page - 1) * per_page])

    cursor.execute(sql_query, params)
    laws = cursor.fetchall()

    # Get total count for pagination
    cursor.execute("SELECT COUNT(*) FROM luat")
    total_count = cursor.fetchone()['COUNT(*)']

    conn.close()

    return jsonify({
        'laws': laws,
        'total_count': total_count,
        'page': page,
        'per_page': per_page
    })

@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory(os.path.join(app.root_path, 'js'), filename)

if __name__ == '__main__':
    app.run(debug=True)
