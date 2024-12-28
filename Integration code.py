import dronekit
from dronekit import connect, VehicleMode, LocationGlobalRelative
import time
import numpy as np
import cv2
import os
import matplotlib.pyplot as plt
import sqlite3
import random

# Connect to the drone
print("Connecting to drone...")
vehicle = connect('127.0.0.1:14550', wait_ready=True)

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

# Function to arm the drone and take off
def arm_and_takeoff(target_altitude):
    print("Arming motors...")
    while not vehicle.is_armable:
        print("Waiting for drone to become armable...")
        time.sleep(1)

    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    while not vehicle.armed:
        print("Waiting for drone to arm...")
        time.sleep(1)

    print("Taking off...")
    vehicle.simple_takeoff(target_altitude)

    while True:
        print(f"Altitude: {vehicle.location.global_relative_frame.alt:.1f}m")
        if vehicle.location.global_relative_frame.alt >= target_altitude * 0.95:
            print("Target altitude reached")
            break
        time.sleep(1)

# Function to capture images using a simulated camera
def capture_images(output_dir, num_images=5):
    print("Capturing images...")
    os.makedirs(output_dir, exist_ok=True)
    for i in range(num_images):
        image = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
        image_path = os.path.join(output_dir, f"image_{i}.jpg")
        cv2.imwrite(image_path, image)
        print(f"Captured {image_path}")
        time.sleep(2)

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

# Function to analyze crop health using NDVI simulation
def analyze_crop_health(input_dir):
    print("Analyzing crop health...")
    ndvi_values = []
    for image_file in sorted(os.listdir(input_dir)):
        if image_file.endswith(".jpg"):
            image_path = os.path.join(input_dir, image_file)
            image = cv2.imread(image_path)
            # Simulated NDVI calculation (Red and NIR bands)
            red_band = image[:, :, 2]
            nir_band = image[:, :, 1] + 50  # Simulated NIR enhancement
            ndvi = (nir_band - red_band) / (nir_band + red_band + 1e-5)
            avg_ndvi = np.mean(ndvi)
            ndvi_values.append(avg_ndvi)
            print(f"{image_file}: NDVI average = {avg_ndvi:.2f}")

    return ndvi_values

# Function for precision planting recommendations
def precision_planting(ndvi_values, threshold=0.4):
    print("Generating precision planting recommendations...")
    recommendations = []
    for i, ndvi in enumerate(ndvi_values):
        if ndvi < threshold:
            recommendation = "Low NDVI detected. Recommend replanting or additional nutrients."
        else:
            recommendation = "Healthy crop detected."
        recommendations.append(recommendation)
        print(f"Image {i}: {recommendation}")

    return recommendations

# Main execution
try:
    # Set parameters
    target_altitude = 10
    image_dir = "drone_images"
    num_images = 10
    database_name = "drone_data.db"
    threshold_value = 0.4

    setup_database(database_name)  # Setup database

    arm_and_takeoff(target_altitude)  # Take off to specified altitude
    capture_images(image_dir, num_images=num_images)  # Capture images for analysis

    ndvi_values = analyze_crop_health(image_dir)  # Analyze crop health
    recommendations = precision_planting(ndvi_values, threshold=threshold_value)  # Generate recommendations

    # Save analyzed data to database
    for image_file, ndvi, recommendation in zip(sorted(os.listdir(image_dir)), ndvi_values, recommendations):
        if image_file.endswith(".jpg"):
            insert_crop_data(image_file, ndvi, recommendation, db_name=database_name)

    print("Returning to Launch")
    vehicle.mode = VehicleMode("RTL")

finally:
    print("Closing vehicle connection")
    vehicle.close()

print("Mission complete.")
