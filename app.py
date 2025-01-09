from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import mysql.connector
import os
from functools import wraps
import logging
from logging.handlers import RotatingFileHandler  

app = Flask(__name__)
app.secret_key = 'your_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
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
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return User(user['id'], user['username'], user['role'])
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
            login_user(User(user['id'], user['username'], user['role']))
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    return render_template('index.html')

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            flash('You do not have permission to perform this action.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/add', methods=['POST'])
@admin_required
def add_law():
    data = request.get_json()
    dieukhoan = data.get('DieuKhoan')
    hinhphat = data.get('HinhPhat')
    phuongtien = data.get('PhuongTien')
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
        flash('Law added successfully!', 'success')
        return jsonify({'success': True, 'message': 'Law added successfully!'})
    except Exception as e:
        conn.rollback()
        flash(f'Error: {str(e)}', 'danger')
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/delete/<int:law_id>', methods=['DELETE'])
@admin_required
def delete_law(law_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    try:
        sql_delete = "DELETE FROM Luat WHERE LuatID = %s"
        cursor.execute(sql_delete, (law_id,))
        conn.commit()
        flash('Law deleted successfully!', 'success')
        return jsonify({'message': 'Law deleted successfully!'})
    except Exception as e:
        conn.rollback()
        flash(f'Error: {str(e)}', 'danger')
        logging.error(f'Error deleting law: {str(e)}', exc_info=True)
        return jsonify({'message': f'Error: {str(e)}'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/update/<int:law_id>', methods=['PUT'])
@admin_required
def update_law(law_id):
    data = request.get_json()
    hinh_phat = data.get('HinhPhat')
    ngay_ap_dung = data.get('NgayApDung')

    if not hinh_phat or not ngay_ap_dung:
        flash('Hình phạt và Ngày Áp Dụng là bắt buộc!', 'danger')
        return jsonify({'message': 'Hình phạt và Ngày Áp Dụng là bắt buộc!'}), 400

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    try:
        # Check if the new HinhPhat exists
        cursor.execute("SELECT HinhPhatID FROM HinhPhat WHERE NoiDung = %s", (hinh_phat,))
        result = cursor.fetchone()

        if result:
            hinhphat_id = result[0]
        else:
            # Insert new HinhPhat and get the new HinhPhatID
            cursor.execute("INSERT INTO HinhPhat (NoiDung) VALUES (%s)", (hinh_phat,))
            hinhphat_id = cursor.lastrowid

        # Update the Luat record with the new HinhPhatID and NgayApDung
        sql_update = """
            UPDATE Luat
            SET HinhPhatID = %s,
                NgayApDung = %s
            WHERE LuatID = %s
        """
        cursor.execute(sql_update, (hinhphat_id, ngay_ap_dung, law_id))
        conn.commit()
        flash('Cập nhật luật thành công!', 'success')
        return jsonify({'message': 'Cập nhật luật thành công!'})
    except Exception as e:
        conn.rollback()
        flash(f'Lỗi: {str(e)}', 'danger')
        logging.error(f'Error updating law: {str(e)}', exc_info=True)
        return jsonify({'message': f'Lỗi: {str(e)}'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('query', '').strip().lower()
    vehicle = request.args.get('vehicle', '').strip().lower()
    penalty = request.args.get('penalty', '').strip().lower()
    page = int(request.args.get('page', 1))
    per_page = 10  # Update to 10 records per page

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql_query = """
        SELECT 
            luat.LuatID,
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
        LEFT JOIN 
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

    sql_query += " LIMIT %s OFFSET %s"
    params.extend([per_page, (page - 1) * per_page])

    cursor.execute(sql_query, params)
    laws = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM luat")
    total_count = cursor.fetchone()['COUNT(*)']

    conn.close()

    return jsonify({
        'laws': laws,
        'total_count': total_count,
        'page': page,
        'per_page': per_page
    })

@app.route('/get_penalty', methods=['GET'])
@login_required
def get_penalty():
    violation = request.args.get('violation', '').strip()
    vehicle = request.args.get('vehicle', '').strip()
    detail = request.args.get('detail', '').strip()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        sql_query = """
            SELECT hinhphat.NoiDung AS HinhPhat, luat.DieuKhoan AS DieuKhoan
            FROM luat
            JOIN loivipham ON loivipham.LoiViPhamID = luat.LoiViPhamID
            JOIN phuongtien ON phuongtien.PhuongTienID = luat.PhuongTienID
            JOIN hinhphat ON hinhphat.HinhPhatID = luat.HinhPhatID
        """
        params = [violation, vehicle]

        if detail and detail != "null":
            sql_query += """
                JOIN chitietloi ON chitietloi.ChiTietLoiID = luat.ChiTietLoiID
                WHERE loivipham.NoiDung = %s AND phuongtien.TenPhuongTien = %s AND chitietloi.NoiDung = %s
            """
            params.append(detail)
        else:
            sql_query += """
                LEFT JOIN chitietloi ON chitietloi.ChiTietLoiID = luat.ChiTietLoiID
                WHERE loivipham.NoiDung = %s AND phuongtien.TenPhuongTien = %s AND luat.ChiTietLoiID IS NULL
            """

        cursor.execute(sql_query, params)
        results = cursor.fetchall()

        if not results:
            return jsonify({'penalties': [{'HinhPhat': 'Không tìm thấy hình phạt', 'DieuKhoan': 'Không tìm thấy điều khoản'}]})

        penalties = [{'HinhPhat': result['HinhPhat'], 'DieuKhoan': result['DieuKhoan']} for result in results]

        return jsonify({'penalties': penalties})
    except Exception as e:
        logging.error(f'Error fetching penalty: {str(e)}', exc_info=True)
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/get_detailed_violations', methods=['GET'])
@login_required
def get_detailed_violations():
    violation = request.args.get('violation', '').strip()
    vehicle = request.args.get('vehicle', '').strip()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        sql_query = """
            SELECT DISTINCT chitietloi.NoiDung AS ChiTietLoi
            FROM luat
            JOIN loivipham ON loivipham.LoiViPhamID = luat.LoiViPhamID
            JOIN phuongtien ON phuongtien.PhuongTienID = luat.PhuongTienID
            LEFT JOIN chitietloi ON chitietloi.ChiTietLoiID = luat.ChiTietLoiID
            WHERE loivipham.NoiDung = %s AND phuongtien.TenPhuongTien = %s
        """
        params = [violation, vehicle]

        cursor.execute(sql_query, params)
        results = cursor.fetchall()

        detailed_violations = list({result['ChiTietLoi'] for result in results if result['ChiTietLoi'] is not None})

        return jsonify({'detailed_violations': detailed_violations})
    except Exception as e:
        logging.error(f'Error fetching detailed violations: {str(e)}', exc_info=True)
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/get_loivipham', methods=['GET'])
@login_required
def get_loivipham():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT NoiDung FROM LoiViPham")
        results = cursor.fetchall()
        loivipham = [result['NoiDung'] for result in results]
        return jsonify({'loivipham': loivipham})
    except Exception as e:
        logging.error(f'Error fetching LoiViPham: {str(e)}', exc_info=True)
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/get_phuongtien', methods=['GET'])
@login_required
def get_phuongtien():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT TenPhuongTien FROM PhuongTien")
        results = cursor.fetchall()
        phuongtien = [result['TenPhuongTien'] for result in results]
        return jsonify({'phuongtien': phuongtien})
    except Exception as e:
        logging.error(f'Error fetching PhuongTien: {str(e)}', exc_info=True)
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory(os.path.join(app.root_path, 'js'), filename)

# Configure logging
if not app.debug:
    handler = RotatingFileHandler('error.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.ERROR)
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

if __name__ == '__main__':
    app.run(debug=True)
