const int analogInPin = A0;
const int LEDPin = 13;

void setup() {                
  pinMode(LEDPin, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  int sensorValue = analogRead(analogInPin);
  Serial.print(sensorValue);
  Serial.print("\n");
  digitalWrite(LEDPin, digitalRead(LEDPin) ^ 1);
  delay(500);
}
