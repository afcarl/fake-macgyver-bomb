const int analogInPin = A0;
const int LEDPin = 13;

void setup() {                
  // initialize the digital pin as an output.
  // Pin 13 has an LED connected on most Arduino boards:
  pinMode(LEDPin, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  int sensorValue = analogRead(analogInPin);
  Serial.print(sensorValue);
  Serial.print("\n");
  digitalWrite(LEDPin, digitalRead(LEDPin) ^ 1);    // set the LED off
  delay(500);              // wait for a second
}
