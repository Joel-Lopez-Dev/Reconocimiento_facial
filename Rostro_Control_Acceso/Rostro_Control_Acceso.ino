#include <LCDIC2.h>
#include <Servo.h>

Servo myservo;
int servoPin = 12;

int ledRojo = 9;
int ledVerde = 10;

bool busy = false;

LCDIC2 lcd(0x27, 16, 2);

#define MSG_BUFFER_SIZE 32
char msgBuffer[MSG_BUFFER_SIZE];
int msgIndex = 0;

unsigned long lastMsgTime = 0;
const unsigned long waitDisplayTime = 2000;

char currentName[MSG_BUFFER_SIZE];  // Nombre que se muestra

void setup() {
  Serial.begin(9600);
  myservo.attach(servoPin);
  myservo.write(0);

  pinMode(ledRojo, OUTPUT);
  pinMode(ledVerde, OUTPUT);

  digitalWrite(ledRojo, HIGH);
  digitalWrite(ledVerde, LOW);

  lcd.begin();
  lcd.clear();
  lcd.print("Esperando acceso");

  currentName[0] = '\0';
  lastMsgTime = millis();
}

void mostrarNombreEnLCD(const char* nombre) {
  lcd.clear();
  lcd.setCursor(0, 0);
  for (int i = 0; i < 16 && nombre[i] != '\0'; i++) {
    lcd.print(nombre[i]);
  }
  if (strlen(nombre) > 16) {
    lcd.setCursor(0, 1);
    for (int i = 16; i < 32 && nombre[i] != '\0'; i++) {
      lcd.print(nombre[i]);
    }
  }
}

void loop() {
  if (busy) {
    // Durante acción, mostrar siempre el nombre y no leer Serial
    mostrarNombreEnLCD(currentName);
    return;
  }

  bool messageReceived = false;

  while (Serial.available() > 0 && !busy) {
    char c = Serial.read();

    if (c == '\n' || c == '\r') {
      if (msgIndex > 0) {
        msgBuffer[msgIndex] = '\0';
        messageReceived = true;
        lastMsgTime = millis();

        if (strcmp(msgBuffer, "4") == 0) {
          if (strlen(currentName) == 0) {
            // Si no hay nombre guardado, ignorar comando
            msgIndex = 0;
            continue;
          }

          busy = true;

          digitalWrite(ledRojo, LOW);
          digitalWrite(ledVerde, HIGH);

          mostrarNombreEnLCD(currentName);

          myservo.write(90);
          delay(4000);
          myservo.write(0);

          digitalWrite(ledRojo, HIGH);
          digitalWrite(ledVerde, LOW);

          busy = false;
          msgIndex = 0;
          break;  // Salir para no procesar más mensajes durante acción
        } else {
          // Guardar el mensaje como nombre
          strncpy(currentName, msgBuffer, MSG_BUFFER_SIZE);
          currentName[MSG_BUFFER_SIZE - 1] = '\0';
          mostrarNombreEnLCD(currentName);
        }

        msgIndex = 0;
      }
    } else {
      if (msgIndex < MSG_BUFFER_SIZE - 1) {
        msgBuffer[msgIndex++] = c;
      }
    }
  }

  if (!messageReceived && !busy && (millis() - lastMsgTime > waitDisplayTime)) {
    if (strlen(currentName) > 0) {
      mostrarNombreEnLCD(currentName);
    } else {
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Esperando acceso");
    }
    lastMsgTime = millis();
  }

  if (!busy && Serial.available() == 0) {
    digitalWrite(ledRojo, HIGH);
    digitalWrite(ledVerde, LOW);
  }
}
