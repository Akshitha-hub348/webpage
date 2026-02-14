from ultralytics import YOLO

model = YOLO("yolov8n.pt")

# COCO vehicle class IDs
VEHICLE_CLASSES = [2, 3, 5, 7]  
# 2=car, 3=motorbike, 5=bus, 7=truck


def detect_vehicles(frame):
    results = model(frame, verbose=False)
    vehicle_count = 0
    boxes_list = []

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            if cls in VEHICLE_CLASSES:
                vehicle_count += 1

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                boxes_list.append((x1, y1, x2, y2))

    return vehicle_count, boxes_list
