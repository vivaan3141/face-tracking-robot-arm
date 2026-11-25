
#include <SoftwareSerial.h>

SoftwareSerial armSerial(10, 11);

const int minLimit[] = {0, 143, 23, 52, 20, 153, 25};
const int maxLimit[] = {0, 663, 977, 978, 978, 845, 773};

const int BASE_ID = 6;
const int TILT_ID = 3;

const int BASE_MIN = 200;
const int BASE_MAX = 773;

const int TILT_MIN = 350;
const int TILT_MAX = 850;

char inputBuffer[32];
byte inputIndex = 0;

void moveServo(uint8_t id, uint16_t position, uint16_t time) {
  if (id < 1 || id > 6) return;

  position = constrain(position, minLimit[id], maxLimit[id]);

  byte buf[10] = {
    0x55, 0x55, 8, 3, 1,
    (byte)(time & 0xFF),
    (byte)(time >> 8),
    id,
    (byte)(position & 0xFF),
    (byte)(position >> 8)
  };

  armSerial.write(buf, 10);
}

void processCommand(char *line) {
  char *comma = strchr(line, ',');
  if (comma == NULL) return;

  *comma = '\0';

  int baseTarget = atoi(line);
  int tiltTarget = atoi(comma + 1);

  baseTarget = constrain(baseTarget, BASE_MIN, BASE_MAX);
  tiltTarget = constrain(tiltTarget, TILT_MIN, TILT_MAX);

  moveServo(BASE_ID, baseTarget, 90);
  moveServo(TILT_ID, tiltTarget, 90);
}

void setup() {
  Serial.begin(9600);
  armSerial.begin(9600);
}

void loop() {
  while (Serial.available() > 0) {
    char c = Serial.read();

    if (c == '\n') {
      inputBuffer[inputIndex] = '\0';

      if (inputIndex > 0) {
        processCommand(inputBuffer);
      }

      inputIndex = 0;
    }
    else if (c != '\r') {
      if (inputIndex < sizeof(inputBuffer) - 1) {
        inputBuffer[inputIndex++] = c;
      }
      else {
        inputIndex = 0;
      }
    }
  }
}
