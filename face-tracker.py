import cv2
import serial
import serial.tools.list_ports
import time

# ARDUINO CONNECTION
ports = serial.tools.list_ports.comports()
port = next(
    (p.device for p in ports
     if "usbmodem" in p.device or "usbserial" in p.device),
    None
)

if port is None:
    print("Arduino not found")
    raise SystemExit

arduino = serial.Serial(port, 9600, timeout=1)
time.sleep(2)

# ARM POSITION
base_pos = 500.0
tilt_pos = 650.0

BASE_MIN, BASE_MAX = 200, 773
TILT_MIN, TILT_MAX = 350, 850

# TRACKING SETTINGS
DEADZONE_X = 95
DEADZONE_Y = 75

BASE_GAIN = 0.45
TILT_GAIN = 0.45

MIN_MOVE = 35
MAX_MOVE = 160

MOVE_INTERVAL = 0.15
CONFIRM_FRAMES = 2
FACE_SMOOTHING = 0.40

INVERT_BASE = False
INVERT_TILT = False

smooth_x = None
smooth_y = None

last_move = 0
confirm_count = 0


def calculate_move(error, deadzone, gain):
    if abs(error) <= deadzone:
        return 0

    remaining = abs(error) - deadzone
    move = remaining * gain

    move = max(MIN_MOVE, min(MAX_MOVE, move))

    return move if error > 0 else -move


# CAMERA
camera = cv2.VideoCapture(0)

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_alt2.xml"
)

print("FACE TRACKER ACTIVE")
print("Press Q to quit")

try:
    while True:
        ret, frame = camera.read()

        if not ret:
            break

        frame = cv2.flip(frame, 1)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.15,
            minNeighbors=6,
            minSize=(65, 65)
        )

        height, width = frame.shape[:2]

        center_x = width // 2
        center_y = height // 2

        # CENTER TARGET ZONE
        cv2.rectangle(
            frame,
            (center_x - DEADZONE_X, center_y - DEADZONE_Y),
            (center_x + DEADZONE_X, center_y + DEADZONE_Y),
            (0, 255, 0),
            2
        )

        if len(faces) > 0:

            x, y, w, h = max(faces, key=lambda f: f[2] * f[3])

            face_x = x + w // 2
            face_y = y + h // 2

            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (255, 0, 0),
                2
            )

            # SMOOTH FACE POSITION
            if smooth_x is None:
                smooth_x = float(face_x)
                smooth_y = float(face_y)
            else:
                smooth_x = (
                    FACE_SMOOTHING * face_x +
                    (1 - FACE_SMOOTHING) * smooth_x
                )

                smooth_y = (
                    FACE_SMOOTHING * face_y +
                    (1 - FACE_SMOOTHING) * smooth_y
                )

            error_x = smooth_x - center_x
            error_y = smooth_y - center_y

            centered = (
                abs(error_x) <= DEADZONE_X and
                abs(error_y) <= DEADZONE_Y
            )

            if centered:
                confirm_count = 0
                status = "CENTERED - STOP"
            else:
                confirm_count += 1
                status = "MOVING"

            # MOVE ARM
            if (
                not centered
                and confirm_count >= CONFIRM_FRAMES
                and time.time() - last_move >= MOVE_INTERVAL
            ):

                base_move = calculate_move(
                    error_x, DEADZONE_X, BASE_GAIN
                )

                tilt_move = calculate_move(
                    error_y, DEADZONE_Y, TILT_GAIN
                )

                if INVERT_BASE:
                    base_move = -base_move

                if INVERT_TILT:
                    tilt_move = -tilt_move

                base_pos += base_move
                tilt_pos += tilt_move

                base_pos = max(
                    BASE_MIN, min(BASE_MAX, base_pos)
                )

                tilt_pos = max(
                    TILT_MIN, min(TILT_MAX, tilt_pos)
                )

                command = f"{int(base_pos)},{int(tilt_pos)}\n"

                arduino.write(command.encode())

                last_move = time.time()
                confirm_count = 0

            cv2.putText(
                frame,
                status,
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

        else:
            confirm_count = 0

            cv2.putText(
                frame,
                "NO FACE",
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2
            )

        cv2.imshow("Face Tracking Robot Arm", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    camera.release()
    cv2.destroyAllWindows()
    arduino.close()
