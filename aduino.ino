#include <Servo.h>

// 핀 번호
#define sone_1 7
#define sone_2 6
#define sone_3 8
Servo servoMotor;
int center = 320;
int position = 90;
int in1 = 12;
int in2 = 11;
int in3 = 4;
int in4 = 5;
int pwmPin = 9;
#define SPEAKER_PIN 6

// 함수 선언
void backward();
void forward();
void stop();
void spin();
void stop2();
void playTone(int frequency, int duration);
void handleSteering(int x_medium);
void handleMovement(int width);
bool parseInput(String input, int &x_medium, int &width);

void setup() {
  // 시리얼 통신 시작
  Serial.begin(9600);
  servoMotor.attach(9);
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  pinMode(in3, OUTPUT);
  pinMode(in4, OUTPUT);
  pinMode(pwmPin, OUTPUT);
  pinMode(SPEAKER_PIN, OUTPUT);
}

void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n'); // 개행 문자까지 읽기
    if (input == "0") {
      stop2();
    } else if (input == "1") {
      stop();
    } else {
      int x_medium, width;
      if (parseInput(input, x_medium, width)) {
        // x_medium 값에 따른 조향 동작
        handleSteering(x_medium);
        
        // width 값에 따른 전진/후진 동작
        handleMovement(width);
      }
    }
  }
}

bool parseInput(String input, int &x_medium, int &width) {
  int commaIndex = input.indexOf(','); // 콤마 위치 찾기
  if (commaIndex > 0) {
    String x_medium_str = input.substring(0, commaIndex); // 콤마 이전 부분
    String width_str = input.substring(commaIndex + 1); // 콤마 이후 부분

    x_medium = x_medium_str.toInt(); // 문자열을 정수로 변환
    width = width_str.toInt(); // 문자열을 정수로 변환
    return true;
  }
  return false;
}

void handle(int x_medium) {
  if (x_medium < center - 50 && x_medium > 0) {
    if (position > 20) {
      if (x_medium < 135) {
        position += 2; 
        spin();
      } else {
        position += 1;
        spin();
      }
    }
  } else if (x_medium > center + 50) {
    if (position < 160) {
      if (x_medium < 505) {
        position -= 1;
        spin();
      } else {
        position -= 2;
        spin();
      }
    }
  } else {
    stop();
  }
}

void Move(int width) {
  if (width < 150 && width > 100) {
    stop();
  } else if (width > 150) {
    backward();
  } else if (width < 100) {
    forward();
  }
}

void backward() {
  digitalWrite(in1, HIGH);
  digitalWrite(in2, LOW);
  digitalWrite(in3, HIGH);
  digitalWrite(in4, LOW);
}

void forward() {
  digitalWrite(in1, LOW);
  digitalWrite(in2, HIGH);
  digitalWrite(in3, LOW);
  digitalWrite(in4, HIGH);
}

void stop() {
  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW);
  digitalWrite(in3, LOW);
  digitalWrite(in4, LOW);
}

void stop2() {
  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW);
  digitalWrite(in3, LOW);
  digitalWrite(in4, LOW);
  delay(3000);
}

void spin() {
  servoMotor.write(position);
}

void playTone(int frequency, int duration) {
  int period = 1000000 / frequency; // 주기 계산
  int pulse = period / 2; // PWM 신호의 펄스 길이 계산
  for (long i = 0; i < duration * 1000L; i += period) {
    digitalWrite(SPEAKER_PIN, HIGH);
    delayMicroseconds(pulse);
    digitalWrite(SPEAKER_PIN, LOW);
    delayMicroseconds(pulse);
  }
}
