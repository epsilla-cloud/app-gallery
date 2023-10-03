import torch
from PIL import Image
import cv2
from transformers import AutoProcessor, CLIPModel
from transformers import BlipProcessor, BlipForConditionalGeneration
from pyepsilla import vectordb
import glob

client = vectordb.Client()
client.load_db(db_name="VideoDB", db_path="/tmp/video-search")
client.use_db(db_name="VideoDB")

device = "cuda" if torch.cuda.is_available() else "cpu"
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
processor = AutoProcessor.from_pretrained("openai/clip-vit-base-patch32")

def encode_frame(frame):

    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    image_input = processor(images=image, return_tensors="pt", padding=True).to(device)
    image_features = model.get_image_features(**image_input)
    return image_features.cpu().detach().numpy()

def extract_frames(video_name, interval=20):
    video_path = './videos/' + video_name
    cap = cv2.VideoCapture(video_path)
    origin_frame_rate = cap.get(5)
    frame_rate = round(origin_frame_rate)
    while cap.isOpened():
        origin_frame_id = cap.get(1)
        frame_id = round(origin_frame_id)
        ret, frame = cap.read()
        if not ret:
            break
        if frame_id % (frame_rate * interval) == 0:
            # Save or process frame
            # print (encode_frame(frame))
            cv2.imwrite('./screenshots/' + video_name + '_' + str(frame_id) + '.jpg', frame)
            # Save the frame to the database
            print(client.insert(
              table_name="VideoData",
              records=[
                {
                    "Name": video_name,
                    "FrameIndex": frame_id,
                    "FrameIndexPrecise": origin_frame_id,
                    "FrameRate": origin_frame_rate,
                    "Embedding": encode_frame(frame)[0].tolist()
                }
              ]
            ))
    cap.release()

def create_vdb_schema():
    client.create_table(
        table_name="VideoData",
        table_fields=[
            {"name": "Name", "dataType": "STRING"},
            {"name": "FrameIndex", "dataType": "INT"},
            {"name": "FrameIndexPrecise", "dataType": "DOUBLE"},
            {"name": "FrameRate", "dataType": "DOUBLE"},
            {"name": "Embedding", "dataType": "VECTOR_FLOAT", "dimensions": 512, "metricType": "COSINE"}
        ]
    )

if __name__ == "__main__":
    create_vdb_schema()
    mp4_files = glob.glob('./videos/*.mp4')
    for mp4_file in mp4_files:
        video_path = mp4_file.rsplit('/', 1)[-1]
        print ('Processing', video_path)
        extract_frames(video_path)
