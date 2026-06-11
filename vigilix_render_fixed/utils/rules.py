import math
from config import CROWD_LIMIT, HIGH_SPEED_PIXEL_THRESHOLD


class RuleEngine:
    def __init__(self):
        self.previous_centers = {}

    def center(self, box):
        x1, y1, x2, y2 = box
        return ((x1 + x2) / 2, (y1 + y2) / 2)

    def distance(self, a, b):
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    def extra_events(self, detections):
        events = []
        persons = [d for d in detections if "person" in d["raw_label"]]
        motorcycles = [d for d in detections if "motorcycle" in d["raw_label"]]

        if len(persons) >= CROWD_LIMIT:
            events.append({"label": "crowd alert", "raw_label": "crowd", "risk": "Medium", "confidence": 0.80, "box": [10, 10, 260, 80], "source": "AI Rule"})

        for moto in motorcycles:
            moto_center = self.center(moto["box"])
            near_people = sum(1 for p in persons if self.distance(moto_center, self.center(p["box"])) < 180)
            if near_people >= 3:
                events.append({"label": "triple riding alert", "raw_label": "triple_riding", "risk": "High", "confidence": 0.78, "box": moto["box"], "source": "AI Rule"})

        for i, det in enumerate(detections):
            if det["raw_label"] not in ["car", "motorcycle", "bus", "truck", "bicycle"]:
                continue
            key = f"{det['raw_label']}_{i}"
            current = self.center(det["box"])
            if key in self.previous_centers:
                speed_pixels = self.distance(current, self.previous_centers[key])
                if speed_pixels > HIGH_SPEED_PIXEL_THRESHOLD:
                    events.append({"label": "high speed alert", "raw_label": "speed", "risk": "Medium", "confidence": min(speed_pixels / 150, 0.99), "box": det["box"], "source": "AI Rule"})
            self.previous_centers[key] = current
        return events
