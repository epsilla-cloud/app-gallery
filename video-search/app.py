import os
import streamlit as st
import torch
from PIL import Image
import cv2
from transformers import AutoProcessor, CLIPModel
from pyepsilla import vectordb

device = "cuda" if torch.cuda.is_available() else "cpu"
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
processor = AutoProcessor.from_pretrained("openai/clip-vit-base-patch32")

client = vectordb.Client()
client.load_db(db_name="VideoDB", db_path="/tmp/video-search")
client.use_db(db_name="VideoDB")

st.title("Video Search App")

user_input_placeholder = st.empty()
user_input = user_input_placeholder.text_input(
    "Describe the content you're looking for:", key="user_input"
)

uploaded_file_placeholder = st.empty()
uploaded_file = uploaded_file_placeholder.file_uploader(
    "Or upload an image:", type=["jpg", "jpeg", "png"], key="uploaded_file"
)

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    image_input = processor(images=image, return_tensors="pt", padding=True).to(device)

if st.button("Search"):
    if user_input:
        text_input = processor(text=user_input, return_tensors="pt", padding=True).to(
            device
        )
        features = model.get_text_features(**text_input)
    elif uploaded_file is not None:
        features = model.get_image_features(**image_input)
    frobenius_norm = torch.norm(features, p="fro")
    normalized_tensor = features / frobenius_norm

    status_code, response = client.query(
        table_name="VideoData",
        query_field="Embedding",
        response_fields=["Name", "FrameIndex", "FrameIndexPrecise", "FrameRate"],
        query_vector=normalized_tensor[0].tolist(),
        limit=30,
        with_distance=True,
    )

    video_screenshots = {}

    for item in response["result"]:
        if item["@distance"] == 0:
            break
        video_name = item["Name"]
        if video_name not in video_screenshots:
            video_screenshots[video_name] = []
        video_screenshots[video_name].append(item)

    for video_name, items in video_screenshots.items():
        st.video("./videos/" + video_name)  # Display the video

        for i in range(0, len(items), 3):  # Step by 3 for 3 columns
            cols = st.columns(3)  # Create 3 columns
            for j, col in enumerate(cols):
                if i + j < len(items):
                    item = items[i + j]
                    frame_rate = item["FrameRate"]
                    frame_index = item["FrameIndex"]
                    frame_index_precise = item["FrameIndexPrecise"]

                    # Calculate the time in seconds, then convert to minutes:seconds format
                    time_seconds = frame_index_precise / frame_rate
                    minutes, seconds = divmod(time_seconds, 60)
                    caption = f"{int(minutes):02d}:{int(seconds):02d}"

                    # Assume get_screenshot is a function that returns an image of the given frame
                    screenshot = (
                        "./screenshots/" + video_name + "_" + str(frame_index) + ".jpg"
                    )
                    col.image(
                        screenshot, caption=caption
                    )  # Display the screenshot with caption
