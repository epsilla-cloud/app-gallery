import streamlit as st
import torch
from PIL import Image
import cv2
from transformers import AutoProcessor, CLIPModel

device = "cuda" if torch.cuda.is_available() else "cpu"
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
processor = AutoProcessor.from_pretrained("openai/clip-vit-base-patch32")

def encode_frame(frame):
    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    image_input = processor(images=image, return_tensors="pt", padding=True).to(device)
    image_features = model.get_image_features(**image_input)
    return image_features.cpu().numpy()

def extract_frames(video_path, interval=10):
    cap = cv2.VideoCapture(video_path)
    frame_rate = cap.get(5)  # Frame rate
    while cap.isOpened():
        frame_id = cap.get(1)  # Current frame number
        ret, frame = cap.read()
        if not ret:
            break
        if frame_id % (frame_rate * interval) == 0:
            # Save or process frame
            pass  # Replace with your code
    cap.release()

# extract_frames('your_video_file.mp4')

st.title("Video Search App")

user_input_placeholder = st.empty()
user_input = user_input_placeholder.text_input("Describe the content you're looking for:", key='user_input')

uploaded_file_placeholder = st.empty()
uploaded_file = uploaded_file_placeholder.file_uploader("Or upload an image:", type=["jpg", "jpeg", "png"], key='uploaded_file')

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    image_input = processor(images=image, return_tensors="pt", padding=True).to(device)

if st.button("Search"):
    if user_input:
        text_input = processor(text=user_input, return_tensors="pt", padding=True).to(device)
        text_features = model.get_text_features(**text_input)
        print (text_features)
    if uploaded_file is not None:
        image_features = model.get_image_features(**image_input)
        print (image_features)

    # Clear the inputs
    st.session_state['user_input'] = ""
    st.session_state['uploaded_file'] = None

    # Assume fetch_videos is a function you've defined to search for videos
    # videos = fetch_videos(text_features, image_features)
    # for video in videos:
    #     st.video(video.url)

# Clear the inputs
# user_input_placeholder.text_input("Describe the content you're looking for:", value="", key='user_input')
# uploaded_file_placeholder.file_uploader("Or upload an image:", type=["jpg", "jpeg", "png"], value=None, key='uploaded_file')

