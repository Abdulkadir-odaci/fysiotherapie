import streamlit as st
from pdf2image import convert_from_path
from streamlit_drawable_canvas import st_canvas
from PIL import Image

st.title("PDF Annotation Page")

# Specify the path to your PDF file
pdf_path = "PSK-meetinstr.pdf"  # Make sure this path is correct

# Convert the first page of the PDF to an image (you can adjust first_page/last_page as needed)
try:
    pages = convert_from_path(pdf_path, dpi=200, first_page=1, last_page=1)
except Exception as e:
    st.error(f"Error converting PDF: {e}")
    pages = []

if pages:
    page_img = pages[0]
    
    # Display the PDF page as an image in Streamlit
    st.image(page_img, caption="PSK Meetinstrument - Instructies", use_column_width=True)
    
    st.markdown("### Annotate the PDF")
    st.markdown("Use the drawing tool below to circle or color areas on the image.")
    
    # Options for the drawing tool
    drawing_mode = st.selectbox("Drawing tool:", ("point", "freedraw", "line", "rect", "circle", "transform"))
    stroke_width = st.slider("Stroke width: ", 1, 25, 3)
    stroke_color = st.color_picker("Stroke color hex: ", "#000000")
    bg_color = st.color_picker("Background color hex: ", "#ffffff")
    
    # Create a canvas overlaying the PDF image.
    # Set canvas dimensions based on the image dimensions.
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",  # Semi-transparent fill for drawn shapes
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color=bg_color,
        update_streamlit=True,
        height=page_img.height,
        width=page_img.width,
        drawing_mode=drawing_mode,
        key="canvas",
    )
    
    st.markdown("### Fill in the required fields")
    # Add text input fields for the areas where users need to provide information.
    activity_1 = st.text_input("Activity 1 (e.g., walking):")
    activity_2 = st.text_input("Activity 2:")
    activity_3 = st.text_input("Activity 3:")
    
    # Process the inputs when the user submits
    if st.button("Submit"):
        st.write("### Submission Summary")
        st.write("**Activity 1:**", activity_1)
        st.write("**Activity 2:**", activity_2)
        st.write("**Activity 3:**", activity_3)
        st.write("**Canvas Data:**", canvas_result.image_data)
else:
    st.error("No pages found in the PDF.")
