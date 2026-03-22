import cv2
import numpy as np
import ezdxf
from shapely.geometry import Polygon
from shapely.affinity import translate
from shapely.ops import unary_union

# Function to create offset contours for manufacturing tolerances
def offset_contour(contour, offset_distance, round_corners=False):
    # Ensure the contour has at least 3 points (plus a closing point to form a Polygon)
    if len(contour) >= 3:
        # Automatically close the contour by adding the first point at the end if not closed
        if not np.array_equal(contour[0], contour[-1]):
            contour = np.vstack([contour, contour[0]])  # Close contour
        
        # Use Shapely to create a polygon from the contour
        poly = Polygon(contour)

        # Apply the offset for manufacturing tolerances
        if round_corners:
            # Buffer with rounding of corners
            offset_poly = poly.buffer(offset_distance, resolution=4)  # Increase resolution for smoother curves
        else:
            # Buffer without rounding corners (sharp edges maintained)
            offset_poly = poly.buffer(offset_distance, join_style=2)  # Join style 2 for sharp edges
        
        return np.array(offset_poly.exterior.coords, dtype=np.int32)
    return None  # Return None if contour is invalid

# Function to nest contours within a fixed canvas (basic nesting logic)
def nest_contours(contours, canvas_width, canvas_height):
    nested_contours = []
    current_x, current_y = 0, 0
    for contour in contours:
        poly = Polygon(contour)
        # Check if the next contour can fit in the remaining canvas space
        if current_x + poly.bounds[2] < canvas_width:
            nested_contours.append(translate(poly, current_x, current_y))
            current_x += poly.bounds[2] + 10  # Add a small gap between parts
        else:
            current_x = 0
            current_y += poly.bounds[3] + 10
            nested_contours.append(translate(poly, current_x, current_y))
    return [np.array(poly.exterior.coords, dtype=np.int32) for poly in nested_contours]

# User settings
offset_distance = 5  # Default offset distance for manufacturing tolerance
round_corners = False  # Whether to round corners

# Ask the user if they want to round corners and set offset distance
def get_user_settings():
    global offset_distance, round_corners

    try:
        # Get offset distance from user
        offset_distance = float(input("Enter offset distance for manufacturing tolerances (positive or negative): "))
    except ValueError:
        print("Invalid input! Using default offset distance of 5.")

    # Ask if the user wants to round corners
    round_input = input("Do you want to round sharp corners? (y/n): ").strip().lower()
    if round_input == 'y':
        round_corners = True
    else:
        round_corners = False

# Open the default camera (usually the first camera, index 0)
cap = cv2.VideoCapture(0)

# Check if the camera opened successfully
if not cap.isOpened():
    print("Error: Could not open camera")
    exit()

# Initialize a counter for image saving
image_counter = 1

# Set canvas size for nesting (in pixels, scaled 1:1 later for DXF)
canvas_width, canvas_height = 1000, 1000

# Get user settings for manufacturing tolerances and corner rounding
get_user_settings()

# Loop to continuously capture frames
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # If frame capture was successful
    if ret:
        # Convert the frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian blur to reduce noise and improve contour detection
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Apply Canny edge detection to find edges (representing the shadow)
        edges = cv2.Canny(blurred, 50, 150)

        # Find contours in the edge map
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Offset and optimize contours (e.g., for manufacturing tolerances)
        optimized_contours = []
        for contour in contours:
            # Offset contour with user-specified tolerance and rounding options
            offset_contour_result = offset_contour(contour[:, 0, :], offset_distance=offset_distance, round_corners=round_corners)
            if offset_contour_result is not None:  # Only add valid contours
                optimized_contours.append(offset_contour_result)

        # Nest contours onto a fixed canvas for efficient material use
        nested_contours = nest_contours(optimized_contours, canvas_width, canvas_height)

        # Create a blank canvas to visualize nested contours
        nested_canvas = np.zeros((canvas_height, canvas_width), dtype=np.uint8)
        for contour in nested_contours:
            cv2.drawContours(nested_canvas, [contour], -1, 255, thickness=1)

        # Display the nested contours in a window
        cv2.imshow('Camera Feed - Press 5 to Capture or q to Exit', nested_canvas)

        # Check for key press every 1 ms
        key = cv2.waitKey(1) & 0xFF
        
        # If '5' is pressed, save the nested contours to a DXF file
        if key == ord('5'):
            # Create a new DXF document
            dxf_filename = f"contour_image_{image_counter}.dxf"
            doc = ezdxf.new(dxfversion='R2010')
            msp = doc.modelspace()

            # Add nested contours to the DXF file
            for contour in nested_contours:
                points = [(point[0], point[1]) for point in contour]
                msp.add_lwpolyline(points)

            # Save the DXF file
            doc.saveas(dxf_filename)
            print(f"DXF file captured and saved as {dxf_filename}")

            # Increment the counter for the next DXF file
            image_counter += 1

        # Break the loop if 'q' is pressed
        if key == ord('q'):
            break
    else:
        print("Error: Failed to capture frame")
        break

# Release the camera and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
