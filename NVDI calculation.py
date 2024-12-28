import cv2
import numpy as np
import os
import matplotlib.pyplot as plt

# Function to calculate NDVI
def calculate_ndvi(red_band, nir_band):
    """
    Calculate the NDVI (Normalized Difference Vegetation Index) using the formula:
    NDVI = (NIR - Red) / (NIR + Red)
    """
    nir_band = nir_band.astype(float)
    red_band = red_band.astype(float)
    ndvi = (nir_band - red_band) / (nir_band + red_band + 1e-5)  # Adding epsilon to avoid division by zero
    return ndvi

# Function to process multispectral images
def process_images(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for image_file in sorted(os.listdir(input_dir)):
        if image_file.endswith(".jpg") or image_file.endswith(".png"):
            # Load image
            image_path = os.path.join(input_dir, image_file)
            image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

            # Assuming the image contains NIR in one channel and Red in another
            # For example: NIR in the first channel and Red in the second channel
            nir_band = image[:, :, 0]  # Replace with the correct channel index for NIR
            red_band = image[:, :, 1]  # Replace with the correct channel index for Red

            # Calculate NDVI
            ndvi = calculate_ndvi(red_band, nir_band)

            # Normalize NDVI to 0-255 for visualization
            ndvi_normalized = cv2.normalize(ndvi, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

            # Save NDVI image
            ndvi_output_path = os.path.join(output_dir, f"ndvi_{image_file}")
            cv2.imwrite(ndvi_output_path, ndvi_normalized)
            print(f"NDVI saved to {ndvi_output_path}")

            # Display NDVI
            plt.imshow(ndvi, cmap="RdYlGn")  # Red-Yellow-Green colormap for vegetation
            plt.colorbar()
            plt.title(f"NDVI for {image_file}")
            plt.show()

# Main execution
if __name__ == "__main__":
    input_directory = "multispectral_images"  # Replace with your input directory containing multispectral images
    output_directory = "ndvi_results"

    if not os.path.exists(input_directory):
        print(f"Input directory '{input_directory}' does not exist. Please add multispectral images.")
    else:
        process_images(input_directory, output_directory)
