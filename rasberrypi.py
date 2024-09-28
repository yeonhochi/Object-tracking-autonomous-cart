import RPi.GPIO as GPIO
import time
import threading
import serial
import cv2
import numpy as np

# 아두이노 시리얼 통신 설정
ser = serial.Serial('/dev/ttyACM0', 9600)

# GPIO 설정GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# 초음파 센서 1
GPIO_TRIGGER1 = 24
GPIO_ECHO1 = 23
GPIO.setup(GPIO_TRIGGER1, GPIO.OUT)
GPIO.setup(GPIO_ECHO1, GPIO.IN)

# 초음파 센서 2
GPIO_TRIGGER2 = 21
GPIO_ECHO2 = 20
GPIO.setup(GPIO_TRIGGER2, GPIO.OUT)
GPIO.setup(GPIO_ECHO2, GPIO.IN)

# 초음파 센서 3
GPIO_TRIGGER3 = 26
GPIO_ECHO3 = 19
GPIO.setup(GPIO_TRIGGER3, GPIO.OUT)
GPIO.setup(GPIO_ECHO3, GPIO.IN)

# 초음파 측정 함수
def measure_distance(trigger_pin, echo_pin):
    GPIO.output(trigger_pin, True)
    time.sleep(0.00001)
    GPIO.output(trigger_pin, False)

    StartTime = time.time()
    StopTime = time.time()

    while GPIO.input(echo_pin) == 0:
        StartTime = time.time()

    while GPIO.input(echo_pin) == 1:
        StopTime = time.time()

    TimeElapsed = StopTime - StartTime
    distance = round((TimeElapsed * 34300) / 2, 2)
    return distance

# 초음파 센서 측정 및 아두이노로 전송하는 함수
def ultrasonic_thread():
    try:
        while True:
            distance1 = measure_distance(GPIO_TRIGGER1, GPIO_ECHO1)
            distance2 = measure_distance(GPIO_TRIGGER2, GPIO_ECHO2)
            distance3 = measure_distance(GPIO_TRIGGER3, GPIO_ECHO3)
            
            print("Distance1 = ", distance1, "cm")
            print("Distance2 = ", distance2, "cm")
            print("Distance3 = ", distance3, "cm")
            
            # 거리가 50cm 미만이면 아두이노로 0을 보냄
            if distance1 < 50 or distance2 < 50 or distance3 < 50:
                ser.write(b'0\n')
            
            time.sleep(1)

    except KeyboardInterrupt:
        pass

# 얼굴 감지기 초기화
chess_cascade = cv2.CascadeClassifier('/home/pi/Desktop/chess_cascade.xml')

# 카메라 초기화
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

_, frame = cap.read()
rows, cols, _ = frame.shape

x_medium = int(cols / 2)
center = int(cols / 2)
object_detected = False
last_detection_time = time.time()

# 얼굴 감지 함수
def face_detection_thread():
    global object_detected
    global last_detection_time

    while True:
        _, frame = cap.read()
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        height, width, _ = frame.shape

        cv2.line(frame, (0, height // 2), (width, height // 2), (0, 0, 255), 2)
        cv2.line(frame, (width // 2, 0), (width // 2, height), (0, 0, 255), 2)
        cv2.line(frame, (width // 2 - 50, 0), (width // 2 - 50, height), (0, 255, 0), 1)
        cv2.line(frame, (width // 2 + 50, 0), (width // 2 + 50, height), (0, 255, 0), 1)

        # 얼굴을 감지합니다.
        object = chess_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=3, minSize=(30, 30))

        # 얼굴이 감지되었을 때
        if len(object) > 0:
            last_detection_time = time.time()  # 객체 감지 시간 갱신

        # 일정 시간(예: 2초) 이상 객체를 감지하지 못한 경우 0을 아두이노로 전송
        if time.time() - last_detection_time >= 0.6:
            ser.write(b'1\n')

        for (x, y, w, h) in object:
            # 바운딩 박스 그리기
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

            # 바운딩 박스의 중심 좌표 계산
            x_medium = int((x + x + w) / 2)
            center_y = int((y + y + h) / 2)

            # 중심에 점 그리기
            cv2.circle(frame, (x_medium, center_y), 5, (255, 0, 0), -1)
            cv2.putText(frame, f'X Medium: {x_medium}', (x, y - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            cv2.putText(frame, f'Width: {w}', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            # Arduino로 중심 x 좌표와 너비를 전송
            ser.write(f'{x_medium},{w}\n'.encode())


        # 프레임 표시
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1)

        # ESC 키를 누르면 루프 종료
        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

# 쓰레드 생성 및 실행
ultrasonic_thread = threading.Thread(target=ultrasonic_thread)
face_detection_thread = threading.Thread(target=face_detection_thread)

ultrasonic_thread.start()
face_detection_thread.start()
