import sqlite3
import os
import random

# Database setup
def setup_database(db_name="drone_data.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS CropData (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_name TEXT NOT NULL,
            ndvi_average REAL NOT NULL,
            recommendation TEXT
        )
    """)
    conn.commit()
    conn.close()

# Insert crop data into database
def insert_crop_data(image_name, ndvi_average, recommendation, db_name="drone_data.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO CropData (image_name, ndvi_average, recommendation)
        VALUES (?, ?, ?)
    """, (image_name, ndvi_average, recommendation))
    conn.commit()
    conn.close()

# Analyze and save crop data
def analyze_and_save_data(input_dir, threshold=0.4, db_name="drone_data.db"):
    print("Analyzing crop health and saving to database...")
    ndvi_values = []
    
    for image_file in sorted(os.listdir(input_dir)):
        if image_file.endswith(".jpg"):
            image_path = os.path.join(input_dir, image_file)
            # Simulated NDVI calculation
            ndvi_avg = random.uniform(0.3, 0.8)  # Replace with real NDVI calculation
            ndvi_values.append(ndvi_avg)
            
            # Generate recommendation
            if ndvi_avg < threshold:
                recommendation = "Low NDVI: Replanting or nutrients needed."
            else:
                recommendation = "Healthy crop."
            
            print(f"{image_file}: NDVI={ndvi_avg:.2f}, Recommendation={recommendation}")
            
            # Save to database
            insert_crop_data(image_file, ndvi_avg, recommendation, db_name=db_name)

# Query and display data
def query_data(db_name="drone_data.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM CropData")
    rows = cursor.fetchall()
    
    print("\nStored Crop Data:")
    print("ID | Image Name | NDVI Average | Recommendation")
    print("-" * 50)
    for row in rows:
        print(f"{row[0]:<3} | {row[1]:<20} | {row[2]:<12.2f} | {row[3]}")
    
    conn.close()

# Main execution
if __name__ == "__main__":
    # Setup
    database_name = "drone_data.db"
    image_dir = "drone_images"
    threshold_value = 0.4

    setup_database(database_name)  # Setup database

    if not os.path.exists(image_dir):
        print(f"Directory '{image_dir}' not found. Please ensure images are available.")
    else:
        analyze_and_save_data(image_dir, threshold=threshold_value, db_name=database_name)  # Analyze and save data
        query_data(database_name)  # Query and display data
