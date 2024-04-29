import cv2
import mediapipe as mp
import websocket

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

# Function to detect if the hand is in a fist
def is_fist(landmarks):
    # Thresholds for determining a fist
    threshold_x = 0.05  # Adjust based on experimentation
    threshold_y = 0.05  # Adjust based on experimentation

    # Check if the fingertips are close to the base of the fingers or the palm
    for i in [8, 12, 16, 20]:  # Tip landmarks for thumb, index, middle, ring, and pinky fingers
        distance_x = abs(landmarks[i].x - landmarks[i - 3].x)
        distance_y = abs(landmarks[i].y - landmarks[i - 3].y)
        if distance_x > threshold_x or distance_y > threshold_y:
            return False
    return True

def is_peace_sign(landmarks):
    # Thresholds for determining if fingers are up or down
    threshold = 0.02  # Adjust based on experimentation

    # Check if index and middle fingers are up and others are down
    # For simplicity, we only check the y-coordinates
    index_finger_up = landmarks[8].y < landmarks[6].y  # 8 is the tip of the index finger
    middle_finger_up = landmarks[12].y < landmarks[10].y  # 12 is the tip of the middle finger
    ring_finger_down = landmarks[16].y > landmarks[14].y  # 16 is the tip of the ring finger
    pinky_finger_down = landmarks[20].y > landmarks[18].y  # 20 is the tip of the pinky

    return index_finger_up and middle_finger_up and ring_finger_down and pinky_finger_down

def update_hit_boxes(screen_width, screen_height):
    hit_box_size = 100  # Adjust the size as needed
    hit_boxes = {
        "left": {
            "x": 0,
            "y": (screen_height - hit_box_size) // 2,
            "width": hit_box_size,
            "height": hit_box_size,
        },
        "right": {
            "x": screen_width - hit_box_size,
            "y": (screen_height - hit_box_size) // 2,
            "width": hit_box_size,
            "height": hit_box_size,
        },
        "up": {
            "x": (screen_width - hit_box_size) // 2,
            "y": 0,
            "width": hit_box_size,
            "height": hit_box_size,
        },
        "down": {
            "x": (screen_width - hit_box_size) // 2,
            "y": screen_height - hit_box_size,
            "width": hit_box_size,
            "height": hit_box_size,
        },
    }
    return hit_boxes

# Initialize Video Capture
cap = cv2.VideoCapture(4)

# Initialize WebSocket connection to the Node.js server
ws = websocket.WebSocket()
ws.connect("ws://localhost:8080")  # Adjust the server URL accordingly

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    screen_width = int(cap.get(3))
    screen_height = int(cap.get(4))

    hit_boxes = update_hit_boxes(screen_width, screen_height)

    for box_name, box in hit_boxes.items():
        cv2.rectangle(frame, (box["x"], box["y"]), (box["x"] + box["width"], box["y"] + box["height"]), (0, 255, 0), 2)

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            # Check if the detected hand is the left hand
            if handedness.classification[0].label == 'Right':
                # Process gestures for right hand
                if is_fist(hand_landmarks.landmark):
                    # Send a message to the Node.js server
                    ws.send("backward")
                elif is_peace_sign(hand_landmarks.landmark):
                    # Send a message to the Node.js server
                    ws.send("forward")

                # Visualize landmarks and check hit boxes
                for landmark in hand_landmarks.landmark:
                    x, y = int(landmark.x * screen_width), int(landmark.y * screen_height)
                    cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

                    for box_name, box in hit_boxes.items():
                        if box["x"] <= x <= box["x"] + box["width"] and box["y"] <= y <= box["y"] + box["height"]:
                            # Send the hit box name as a message to the Node.js server
                            ws.send(box_name)

    cv2.imshow('Hand Tracking', frame)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

