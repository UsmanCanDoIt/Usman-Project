from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

DATABASE = 'drone_data.db'

# Function to query the database
def query_database(query, args=(), one=False):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(query, args)
    result = cursor.fetchall()
    conn.close()
    return (result[0] if result else None) if one else result

# Function to add new records to the database
def insert_into_database(image_name, ndvi_average, recommendation):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO CropData (image_name, ndvi_average, recommendation)
        VALUES (?, ?, ?)
    """, (image_name, ndvi_average, recommendation))
    conn.commit()
    conn.close()

# Route to get all crop data
@app.route('/crop-data', methods=['GET'])
def get_crop_data():
    data = query_database("SELECT * FROM CropData")
    return jsonify([
        {"id": row[0], "image_name": row[1], "ndvi_average": row[2], "recommendation": row[3]}
        for row in data
    ])

# Route to add crop data
@app.route('/crop-data', methods=['POST'])
def add_crop_data():
    if not request.json or 'image_name' not in request.json or 'ndvi_average' not in request.json:
        return jsonify({"error": "Invalid input"}), 400

    image_name = request.json['image_name']
    ndvi_average = request.json['ndvi_average']
    recommendation = request.json.get('recommendation', "No recommendation")
    
    insert_into_database(image_name, ndvi_average, recommendation)
    return jsonify({"message": "Crop data added successfully"}), 201

# Route to get crop data by ID
@app.route('/crop-data/<int:crop_id>', methods=['GET'])
def get_crop_data_by_id(crop_id):
    data = query_database("SELECT * FROM CropData WHERE id = ?", [crop_id], one=True)
    if data:
        return jsonify({"id": data[0], "image_name": data[1], "ndvi_average": data[2], "recommendation": data[3]})
    else:
        return jsonify({"error": "Crop data not found"}), 404

# Route to delete crop data by ID
@app.route('/crop-data/<int:crop_id>', methods=['DELETE'])
def delete_crop_data(crop_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM CropData WHERE id = ?", [crop_id])
    conn.commit()
    conn.close()
    return jsonify({"message": "Crop data deleted successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
