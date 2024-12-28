import dronekit
from dronekit import connect, VehicleMode, LocationGlobalRelative
import time
import numpy as np
import cv2
import os
import matplotlib.pyplot as plt

# Connect to the drone
print("Connecting to drone...")
vehicle = connect('127.0.0.1:14550', wait_ready=True)

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
    
    # Plot NDVI results
    plt.figure(figsize=(10, 5))
    plt.plot(ndvi_values, marker='o', label='NDVI Average')
    plt.title('Crop Health Analysis')
    plt.xlabel('Image Index')
    plt.ylabel('NDVI Average')
    plt.legend()
    plt.grid()
    plt.show()

# Function for precision planting recommendations
def precision_planting(ndvi_values, threshold=0.4):
    print("Generating precision planting recommendations...")
    for i, ndvi in enumerate(ndvi_values):
        if ndvi < threshold:
            print(f"Image {i}: Low NDVI detected. Recommend replanting or additional nutrients.")
        else:
            print(f"Image {i}: Healthy crop detected.")

# Main execution
try:
    # Set parameters
    target_altitude = 10
    image_dir = "drone_images"
    num_images = 10

    arm_and_takeoff(target_altitude)  # Take off to specified altitude
    capture_images(image_dir, num_images=num_images)  # Capture images for analysis
    analyze_crop_health(image_dir)  # Analyze crop health

    # Simulate NDVI values for recommendation
    ndvi_values = [np.random.uniform(0.3, 0.8) for _ in range(num_images)]
    precision_planting(ndvi_values)

    print("Returning to Launch")
    vehicle.mode = VehicleMode("RTL")

finally:
    print("Closing vehicle connection")
    vehicle.close()

print("Mission complete.")
