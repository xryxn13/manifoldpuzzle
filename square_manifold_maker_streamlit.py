import streamlit as st
from PIL import Image
import io
import zipfile

# Function to resize an image to 500x500 and split it into 16 parts of 125x125
def split_image(image_path):
    image = Image.open(image_path)
    image = image.resize((500, 500))
    
    part_size = 125
    parts = {}
    
    for row in range(4):
        for col in range(4):
            left = col * part_size
            top = row * part_size
            right = left + part_size
            bottom = top + part_size
            part = image.crop((left, top, right, bottom))
            parts[(row, col)] = part
    
    return parts

# Function to rotate the image part based on the specified angle
def rotate_image(image_part, angle):
    return image_part.rotate(angle, expand=True)

# Function to create an 8x8 grid and place image parts at specified positions
def create_grid(image1_parts, image2_parts, other_images, layout, grid_size=9):
    grid_image = Image.new("RGB", (grid_size * 125, grid_size * 125), (255, 255, 255))

    for row in range(grid_size):
        for col in range(grid_size):
            part_code = layout[row][col]

            angle = 0  # Default angle is 0 (no rotation)

            if '-' in part_code:
                parts = part_code.split('-')
                if len(parts) == 3:
                    part_code = f"{parts[0]}-{parts[1]}"  # Remove the angle from part code
                    angle = int(parts[2])  # Get the rotation angle

            if part_code.startswith("1-"):
                index = int(part_code.split("-")[1]) - 1
                image_part = image1_parts[(index // 4, index % 4)]
            elif part_code.startswith("2-"):
                index = int(part_code.split("-")[1]) - 1
                image_part = image2_parts[(index // 4, index % 4)]
            elif part_code == "o":
                image_part = other_images  # Use the "other" image

            if angle != 0:
                image_part = rotate_image(image_part, angle)

            grid_image.paste(image_part, (col * 125, row * 125))

    return grid_image

# Define multiple layouts as placeholders
layouts01 = {
    "Layout 1": [
        ["o", "o", "1-9", "1-10", "1-11", "1-12", "o", "o", "o"],
        ["", "", "1-13", "1-14", "1-15", "1-16", "o", "o", "o"],
        ["", "", "2-1", "2-2", "2-3", "2-4", "o", "o", "o"],
        ["", "",  "2-5", "2-6", "2-7", "2-8", "o", "o", "o"],
        ["o", "o", "2-9", "2-10", "2-11", "2-12",  "1-8-180", "1-7-180", "1-6-180"],
        ["o", "o", "2-13", "2-14", "2-15", "2-16", "1-4-180", "1-3-180", "1-2-180"],
        ["o", "o", "1-1", "o", "o", "o",  "o", "o", "o"],
        ["o", "o", "1-5", "o", "o", "o", "o", "o", "o"],
        ["o", "o", "o", "o", "o", "o", "o", "o", "o"]
    ],
    "Layout 2": [
        ["o", "o", "o", "o", "o", "o", "o", "o", "o"],
        ["1-9", "o", "o", "o", "1-10", "1-11", "o", "o", "1-12"],
        ["1-13", "o", "o", "o", "1-14", "1-15", "o", "o", "1-16"],
        ["2-1", "o", "o", "o", "2-2", "2-3", "o", "o", "2-4"],
        ["2-5", "o", "o", "o", "2-6", "2-7", "o", "o", "2-8"],
        ["2-9", "o", "o", "o", "2-10", "2-11", "o", "o", "2-12"],
        ["2-13", "o", "o", "o", "2-14", "2-15", "o", "o", "2-16"],
        ["1-1", "o", "o", "o", "1-2", "1-3", "o", "o", "1-4"],
        ["1-5", "o", "o", "o", "1-6", "1-7", "o", "o", "1-8"]
    ],
    "Layout 3": [
        ["o", "o", "o", "1-9", "1-10", "1-11", "1-12", "o", "o"],
        ["o", "o", "o", "1-13", "1-14", "1-15", "1-16", "o", "o"],
        ["o", "o", "o", "2-1", "2-2", "2-3", "2-4", "o", "o"],
        ["o", "o", "o", "2-5", "2-6", "2-7", "2-8", "o", "o"],
        ["o", "o", "o", "2-9", "2-10", "2-11", "2-12", "o", "o"],
        ["o", "o", "o", "2-13", "2-14", "2-15", "2-16", "o", "o"],
        ["o", "o", "o", "1-1", "1-2", "1-3", "1-4", "o", "o"],
        ["o", "o", "o", "1-5", "1-6", "1-7", "1-8", "o", "o"],
        ["o", "o", "o", "o", "o", "o", "o", "o", "o"]
    ],
    "Layout 4": [
        ["o", "2-15-180", "2-14-180", "2-13-180", "1-1", "1-2", "1-3", "1-4", "2-16-180"],
        ["o", "2-11-180", "2-10-180", "2-9-180", "1-5", "1-6", "1-7", "1-8", "2-12-180"],
        ["o", "o", "o", "o", "1-9", "1-10", "1-11", "1-12", "o"],
        ["o", "o", "o", "o", "1-13", "1-14", "1-15", "1-16", "o"],
        ["o", "o", "o", "o", "2-1", "2-2", "2-3", "2-4", "o"],
        ["o", "o", "o", "o", "o", "o", "o", "o", "o"],
        ["o", "2-7-180", "2-6-180", "2-5-180", "o", "o", "o", "o", "2-8-180"],
        ["o", "o", "o", "o", "o", "o", "o", "o", "o"],
        ["o", "o", "o", "o", "o", "o", "o", "o", "o"]
    ],
}
layouts02 = {
    "Layout 1": [
        ["o", "1-5", "o", "1-6", "o", "1-7", "o", "o", "o"],
        ["o", "1-9", "o", "1-10", "o", "1-11", "o", "o", "1-12"],
        ["o", "1-13", "o", "1-14", "o", "1-15", "o", "o", "1-16"],
        ["o", "2-1", "o", "2-2", "o", "2-3", "o", "o", "2-4"],
        ["o", "2-5", "o", "2-6", "o", "2-7", "o", "o", "2-8"],
        ["o", "2-9", "o", "2-10", "o", "2-11", "o", "o", "2-12"],
        ["o", "2-13", "o", "2-14", "o", "2-15", "o", "o", "2-16"],
        ["o", "1-1", "o", "1-2", "o", "1-3", "o", "o", "1-4"],
        ["o", "o", "o", "o", "o", "o", "o", "o", "1-8"]
    ],
    "Layout 2": [
        ["2-1", "2-2", "2-3", "2-4", "o", "o", "o", "o", "1-13-270"],
        ["2-5", "2-6", "2-7", "2-8", "o", "o", "o", "o", "1-14-270"],
        ["2-9", "2-10", "2-11", "2-12", "o", "o", "o", "o", "1-15-270"],
        ["2-13", "2-14", "2-15", "2-16", "o", "o", "o", "o", "1-16-270"],
        ["o", "o", "o", "o", "1-4-90", "1-8-90", "1-12-90", "o", "o"],
        ["o", "o", "o", "o", "1-3-90", "1-7-90", "1-11-90", "o", "o"],
        ["o", "o", "o", "o", "1-2-90", "1-6-90", "1-10-90", "o", "o"],
        ["o", "o", "o", "o", "o", "o", "o", "o", "o"],
        ["o", "1-9-270", "1-5-270", "1-1-270", "o", "o", "o", "o", "o"]
    ],
    "Layout 3": [
        ["o", "o", "2-9", "2-10", "2-11", "2-12", "o", "o", "o"],
        ["o", "o", "o", "o", "o", "o", "o", "o", "o"],
        ["o", "o", "2-13", "2-14", "2-15", "2-16", "o", "o", "o"],
        ["o", "o", "1-1", "1-2", "1-3", "1-4", "o", "o", "o"],
        ["o", "o", "1-5", "1-6", "1-7", "1-8", "o", "o", "o"],
        ["2-6-180", "2-5-180", "1-9", "1-10", "1-11", "1-12", "o", "o", "o"],
        ["2-2-180", "2-1-180", "1-13", "1-14", "1-15", "1-16", "o", "o", "o"],
        ["o", "o", "o", "o", "o", "o", "2-4-90", "2-8-90", "o"],
        ["o", "o", "o", "o", "o", "o", "2-3-90", "2-7-90", "o"]
    ]
}
layouts03 = {
    "Layout 1": [
        ["o", "1-1-90", "1-5-90", "1-9-90", "1-13-90", "o", "o", "o", "o"],
        ["2-13-180", "o", "o", "o", "o", "o", "o", "o", "o"],
        ["2-9-180", "o", "o", "o", "o", "1-14-270", "1-10-270", "1-6-270", "1-2-270"],
        ["2-5-180", "o", "o", "o", "o", "1-15-270", "1-11-270", "1-7-270", "1-3-270"],
        ["2-1-180", "o", "o", "o", "o", "1-16-270", "1-12-270", "1-8-270", "1-4-270"],
        ["o", "o", "2-2", "2-3", "2-4", "o", "o", "o", "o"],
        ["o", "o", "2-6", "2-7", "2-8", "o", "o", "o", "o"],
        ["o", "o", "2-10", "2-11", "2-12", "o", "o", "o", "o"],
        ["o", "o", "2-14", "2-15", "2-16", "o", "o", "o", "o"]
    ],

    "Layout 2": [
        ["o", "o", "o", "o", "o", "o", "o", "2-15-270", "o"],
        ["o", "o", "o", "o", "o", "o", "o", "2-16-270", "2-12-270"],
        ["o", "2-14-180", "2-13-180", "1-1", "1-2", "1-3", "1-4", "o", "o"],
        ["o", "o", "o", "1-5", "1-6", "1-7", "1-8", "o", "o"],
        ["o", "o", "o", "1-9", "1-10", "1-11", "1-12", "o", "o"],
        ["o", "o", "o", "1-13", "1-14", "1-15", "1-16", "o", "o"],
        ["2-9-270", "2-5-270", "2-1-270", "o", "o", "o", "o", "2-4-90", "2-8-90"],
        ["2-10-270", "2-6-270", "2-2-270", "o", "o", "o", "o", "o", "o"],
        ["2-11-270", "2-7-270", "2-3-270", "o", "o", "o", "o", "o", "o"]
    ],

    "Layout 3": [
        ["o", "o", "o", "o", "o", "o", "o", "2-15-270", "2-11-270"],
        ["2-10-90", "2-14-90", "o", "o", "o", "o", "o", "2-16-270", "2-12-270"],
        ["2-9-90", "2-13-90", "o", "o", "o", "o", "o", "o", "o"],
        ["o", "o", "1-1", "1-2", "1-3", "1-4", "o", "o", "o"],
        ["o", "o", "1-5", "1-6", "1-7", "1-8", "o", "o", "o"],
        ["o", "o", "1-9", "1-10", "1-11", "1-12", "o", "o", "o"],
        ["o", "o", "1-13", "1-14", "1-15", "1-16", "o", "o", "o"],
        ["2-5-270", "2-1-270", "o", "o", "o", "o", "2-4-90", "2-8-90", "o"],
        ["2-6-270", "2-2-270", "o", "o", "o", "o", "2-3-90", "2-7-90", "o"]
    ],
}

# Streamlit UI
st.title('Generate Multiple Layout Images')

# Upload images
image1_file = st.file_uploader("Upload Image 1", type=["png", "jpg", "jpeg"])
image2_file = st.file_uploader("Upload Image 2", type=["png", "jpg", "jpeg"])

if image1_file and image2_file:
    # Load and process the uploaded images
    image1_parts = split_image(image1_file)
    image2_parts = split_image(image2_file)
    option = st.selectbox("Select Level", [1, 2, 3])
    
    # Load the "other image" from the local folder (adjust the folder path as needed)
    other_image_path = "other_image1.png"  # Adjust this path to your folder
    other_image = Image.open(other_image_path)
    other_image = other_image.resize((125, 125))  # Resize the other image to 125x125
    if option == 1:
        for layout_name, layout in layouts01.items():
            st.subheader(f"{layout_name}")

            # Generate the grid image based on the layout
            final_image = create_grid(image1_parts, image2_parts, other_image, layout)

            # Display the final image
            st.image(final_image, caption=f"{layout_name} Grid Image", use_container_width=True)

            # Convert the final image to PNG for download
            img_byte_arr = io.BytesIO()
            final_image.save(img_byte_arr, format="PNG")
            img_byte_arr = img_byte_arr.getvalue()

            # Allow the user to download the final image
            st.download_button(
                label=f"Download {layout_name} Image as PNG",
                data=img_byte_arr,
                file_name=f"{layout_name}_grid_image.png",
                mime="image/png"
            )
    elif option == 2:
        for layout_name, layout in layouts02.items():
            st.subheader(f"{layout_name}")

            # Generate the grid image based on the layout
            final_image = create_grid(image1_parts, image2_parts, other_image, layout)

            # Display the final image
            st.image(final_image, caption=f"{layout_name} Grid Image", use_container_width=True)

            # Convert the final image to PNG for download
            img_byte_arr = io.BytesIO()
            final_image.save(img_byte_arr, format="PNG")
            img_byte_arr = img_byte_arr.getvalue()

            # Allow the user to download the final image
            st.download_button(
                label=f"Download {layout_name} Image as PNG",
                data=img_byte_arr,
                file_name=f"{layout_name}_grid_image.png",
                mime="image/png"
            )


    elif option == 3:
        for layout_name, layout in layouts03.items():
            st.subheader(f"{layout_name}")

            # Generate the grid image based on the layout
            final_image = create_grid(image1_parts, image2_parts, other_image, layout)

            # Display the final image
            st.image(final_image, caption=f"{layout_name} Grid Image", use_container_width=True)

            # Convert the final image to PNG for download
            img_byte_arr = io.BytesIO()
            final_image.save(img_byte_arr, format="PNG")
            img_byte_arr = img_byte_arr.getvalue()

            # Allow the user to download the final image
            st.download_button(
                label=f"Download {layout_name} Image as PNG",
                data=img_byte_arr,
                file_name=f"{layout_name}_grid_image.png",
                mime="image/png"
            )
