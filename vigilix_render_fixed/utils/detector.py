import os
import cv2
from config import ROBOFLOW_API_KEY, ROBOFLOW_MODELS, CONFIDENCE

CUSTOM_MODEL = "models/threat_detector.pt"

HIGH_RISK_WORDS = {
    "weapon", "gun", "knife", "fire", "smoke", "fight", "violence",
    "theft", "steal", "stealing", "no_helmet", "no helmet", "without helmet",
    "no_seatbelt", "no seatbelt", "without seat belt", "triple_riding", "triple riding", "sharp object"
}

MEDIUM_RISK_WORDS = {
    "bottle", "restricted item", "alcohol", "cigarette", "smoking", "running",
    "helmet", "motorcycle", "person", "car", "crowd", "speed"
}


class HybridDetector:
    def __init__(self):
        self.local_ready = False
        self.local_model = None
        self.local_names = {}
        self.cloud_ready = False
        self.cloud_client = None
        self.cloud_model_ids = []
        self.load_local_yolo()
        self.load_cloud_models()

    def load_local_yolo(self):
        try:
            from ultralytics import YOLO
            self.local_model = YOLO(CUSTOM_MODEL) if os.path.exists(CUSTOM_MODEL) else YOLO("yolov8n.pt")
            self.local_names = self.local_model.names
            self.local_ready = True
        except Exception as e:
            print("AI loading failed:", e)
            self.local_ready = False

    def load_cloud_models(self):
        model_ids = [m for m in ROBOFLOW_MODELS.values() if m]
        if not ROBOFLOW_API_KEY or not model_ids:
            self.cloud_ready = False
            return
        try:
            from inference_sdk import InferenceHTTPClient
            self.cloud_client = InferenceHTTPClient(api_url="https://serverless.roboflow.com", api_key=ROBOFLOW_API_KEY)
            self.cloud_model_ids = model_ids
            self.cloud_ready = True
        except Exception as e:
            print("Cloud AI loading failed:", e)
            self.cloud_ready = False

    def risk_level(self, label):
        text = label.lower().replace("-", "_")
        if any(word in text for word in HIGH_RISK_WORDS):
            return "High"
        if any(word in text for word in MEDIUM_RISK_WORDS):
            return "Medium"
        return "Low"

    def detect_local(self, frame):
        detections = []
        if not self.local_ready or self.local_model is None:
            return detections
        results = self.local_model(frame, conf=CONFIDENCE, verbose=False)
        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                label = self.local_names.get(cls_id, str(cls_id)).lower()
                conf = float(box.conf[0])
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                display_label = label
                if label == "bottle":
                    display_label = "bottle / restricted item"
                elif label == "knife":
                    display_label = "knife / sharp object"
                detections.append({
                    "label": display_label,
                    "raw_label": label,
                    "box": [x1, y1, x2, y2],
                    "confidence": conf,
                    "risk": self.risk_level(display_label),
                    "source": "AI"
                })
        return detections

    def detect_cloud(self, frame):
        detections = []
        if not self.cloud_ready:
            return detections
        temp_path = "temp_frame.jpg"
        cv2.imwrite(temp_path, frame)
        for model_id in self.cloud_model_ids:
            try:
                result = self.cloud_client.infer(temp_path, model_id=model_id)
                for p in result.get("predictions", []):
                    label = str(p.get("class", "object")).lower()
                    conf = float(p.get("confidence", 0))
                    x = float(p.get("x", 0)); y = float(p.get("y", 0))
                    width = float(p.get("width", 0)); height = float(p.get("height", 0))
                    detections.append({
                        "label": label,
                        "raw_label": label,
                        "box": [x - width / 2, y - height / 2, x + width / 2, y + height / 2],
                        "confidence": conf,
                        "risk": self.risk_level(label),
                        "source": "AI"
                    })
            except Exception as e:
                print("Cloud inference error:", e)
        return detections

    def detect(self, frame):
        return self.detect_local(frame) + self.detect_cloud(frame)
