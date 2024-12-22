from flask import Flask, render_template, request, jsonify
import mysql.connector

app = Flask(__name__)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Phanvylqd@112',
    'database': 'traffic_laws_db',
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
    query = request.args.get('query', '').lower()  
    vehicle = request.args.get('vehicle', '').lower()  
    penalty = request.args.get('penalty', '')  
    violation_description = request.args.get('violation_description', '').lower()  

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql_query = """SELECT 
                        l.LawID,
                        v.ViolationName,
                        p.PenaltyAmount,
                        vt.VehicleTypeName,
                        v.Description AS ViolationDescription,
                        l.LawNumber,
                        v.ViolationName,
                        l.EffectiveDate
                   FROM 
                        Laws l
                   JOIN 
                        Violations v ON l.LawID = v.LawID
                   JOIN 
                        Penalties p ON v.ViolationID = p.ViolationID
                   JOIN 
                        ViolationVehicles vv ON v.ViolationID = vv.ViolationID
                   JOIN 
                        Vehicles vt ON vv.VehicleTypeID = vt.VehicleTypeID
                   WHERE 
                        v.ViolationName LIKE %s COLLATE utf8mb4_unicode_ci
                   """
    
    params = [f"%{query}%"]
    if vehicle:
        sql_query += " AND vt.VehicleTypeName LIKE %s COLLATE utf8mb4_unicode_ci"
        params.append(f"%{vehicle}%")
    if penalty:
        sql_query += " AND p.PenaltyAmount = %s"
        params.append(penalty)
    if violation_description:
        sql_query += " AND v.Description LIKE %s COLLATE utf8mb4_unicode_ci"
        params.append(f"%{violation_description}%")

    cursor.execute(sql_query, params)
    laws = cursor.fetchall()
    conn.close()

    return jsonify(laws)

if __name__ == '__main__':
    app.run(debug=True)
