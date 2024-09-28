#Raspberry Pi와 Arduino를 이용한 초음파 센서 및 얼굴 인식 시스템 구축
#이 글에서는 Raspberry Pi, 초음파 센서, 그리고 OpenCV를 사용하여 초음파 거리 측정과 얼굴 인식을 통해 Arduino에 명령을 전달하는 시스템을 구축하는 방법을 설명합니다. 
#이 시스템은 초음파 센서로 주변의 물체와의 거리를 측정하고, OpenCV를 통해 얼굴이나 물체를 인식한 후, 그 데이터를 Arduino로 전송합니다.
#이를 통해 일정 조건이 충족되면 Arduino로 명령을 보내 다양한 작업을 수행할 수 있습니다.

프로젝트 개요
이 프로젝트는 두 가지 주요 기능을 수행합니다:

초음파 거리 측정: 세 개의 초음파 센서를 사용하여 물체와의 거리를 측정합니다. 거리가 설정된 임계값보다 작아지면 Arduino로 명령을 보냅니다.
얼굴 인식: OpenCV를 사용하여 카메라로 객체(이 경우 얼굴 또는 체스 조각)를 인식하고 그 정보를 Arduino로 전달합니다. 일정 시간 동안 객체를 인식하지 못하면 다른 명령을 보냅니다.
1. 아두이노와 Raspberry Pi 간의 시리얼 통신 설정
먼저 Raspberry Pi와 Arduino 사이의 시리얼 통신을 설정합니다. Raspberry Pi는 serial 라이브러리를 사용하여 Arduino와 데이터를 주고받습니다. 아래 코드는 Raspberry Pi에서 시리얼 포트를 열어 통신을 시작하는 부분입니다.

ser = serial.Serial('/dev/ttyACM0', 9600)
여기서 /dev/ttyACM0는 Arduino가 연결된 포트입니다. 이 설정으로 Raspberry Pi는 9600bps의 속도로 Arduino와 데이터를 송수신할 수 있습니다.

2. 초음파 센서 설정 및 거리 측정
초음파 센서는 물체와의 거리를 측정하는 데 사용됩니다. 총 세 개의 초음파 센서를 GPIO 핀에 연결합니다.


GPIO_TRIGGER1 = 24
GPIO_ECHO1 = 23
GPIO.setup(GPIO_TRIGGER1, GPIO.OUT)
GPIO.setup(GPIO_ECHO1, GPIO.IN)
위와 같은 방식으로 두 번째, 세 번째 센서도 설정해줍니다.

거리 측정 함수
초음파 센서로부터 거리 데이터를 얻기 위해 measure_distance() 함수를 정의했습니다. 이 함수는 초음파 신호를 보내고 반사되어 돌아오는 시간을 측정하여 거리를 계산합니다.

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



Trigger 핀에 짧은 펄스를 보내 초음파를 발생시키고, Echo 핀에서 신호를 받아 돌아오는 시간을 측정합니다.
시간을 이용하여 물체와의 거리를 계산하며, 그 결과는 cm 단위로 반환됩니다.
센서 데이터를 기반으로 Arduino로 명령 전송
초음파 센서로부터 측정된 거리가 50cm 이하인 경우 Arduino로 0 값을 전송하여 특정 동작을 유발합니다.


if distance1 < 50 or distance2 < 50 or distance3 < 50:
    ser.write(b'0\n')
    
3. 얼굴 인식 및 객체 추적
OpenCV를 이용한 얼굴 감지기 설정
OpenCV의 CascadeClassifier를 사용하여 얼굴 인식을 수행합니다. 여기서는 커스텀 캐스케이드 분류기 파일을 사용하여 체스 조각을 감지할 수도 있습니다.

python
코드 복사
chess_cascade = cv2.CascadeClassifier('/home/pi/Desktop/chess_cascade.xml')
얼굴 인식 로직
카메라로부터 실시간으로 프레임을 읽고, 이를 회색조로 변환한 후, 얼굴이나 객체를 감지합니다.

gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
object = chess_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=3, minSize=(30, 30))
감지된 객체의 좌표를 바탕으로 중앙 좌표를 계산하고, 그 값을 Arduino로 전송합니다.

x_medium = int((x + x + w) / 2)
ser.write(f'{x_medium},{w}\n'.encode())
객체가 감지되지 않은 경우에는 일정 시간 동안 감지되지 않았음을 인식하고 Arduino로 1 값을 전송합니다.


if time.time() - last_detection_time >= 0.6:
    ser.write(b'1\n')
4. 멀티스레딩을 통한 병렬 처리
이 프로젝트는 초음파 거리 측정과 얼굴 인식을 동시에 처리해야 합니다. 이를 위해 Python의 threading 라이브러리를 사용하여 두 개의 쓰레드를 생성합니다.

python
코드 복사
ultrasonic_thread = threading.Thread(target=ultrasonic_thread)
face_detection_thread = threading.Thread(target=face_detection_thread)

ultrasonic_thread.start()
face_detection_thread.start()
이렇게 하면 초음파 센서와 얼굴 인식이 각각 독립적인 스레드에서 실행되어 병렬로 데이터를 처리할 수 있습니다.

결론
이 프로젝트를 통해 Raspberry Pi와 Arduino를 결합하여 초음파 센서 및 얼굴 인식 기능을 구현할 수 있습니다. 
초음파 센서는 물체와의 거리를 측정하고, OpenCV는 실시간으로 얼굴을 감지하여 그 정보를 Arduino에 전달합니다. 
이를 통해 다양한 IoT 및 로봇 공학 프로젝트에 활용할 수 있는 시스템을 만들 수 있습니다.
