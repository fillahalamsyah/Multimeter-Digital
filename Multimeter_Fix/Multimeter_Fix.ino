#include <Wire.h> 
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27,16,2);  // set the LCD address to 0x27 for a 16 chars and 2 line display

int Pin_Ampere = A0; // Pin Analog Input Amperemeter
int Pin_Volt1 = A1; // Pin Analog Input Voltmeter 1

// Fungsi untuk membaca nilai arus pada rangkaian Amperemeter
float Amperemeter(int Pin){
  float RA = 1000;             // Resistor Sensor Amperemeter
  float ADC_I = analogRead(Pin); // Baca nilai analog
  float VadcI = 5*ADC_I/1023;   // Voltase ADC
  float I_ukur = VadcI/RA;     // Arus dalam Ampere (A)
  return I_ukur*1000;
}

// Fungsi untuk membaca nilai tegangan pada rangkaian Voltmeter
float Voltmeter(int Pin){
  float RV1 = 1000;      // Resistor 1 Voltmeter 1k
  float RV2 = 1000;        // Resistor 2 Voltmeter 1k
  float ADC_V = analogRead(Pin);  // Baca nilai analog 
  float VadcV = 5*ADC_V/1023;  // Voltase ADC
  float V_ukur = VadcV*(RV1+RV2)/RV2;// Tegangan terukur dalam Volt
  return V_ukur;
}

void setup() {     
  Serial.begin(9600);
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0,0); lcd.print("   Multimeter");
  lcd.setCursor(0,1); lcd.print("     Digital");

  pinMode(Pin_Ampere,INPUT);
  pinMode(Pin_Volt1,INPUT);
  pinMode(3, OUTPUT);pinMode(4, OUTPUT);pinMode(5, OUTPUT);pinMode(6, OUTPUT);pinMode(7, OUTPUT);
  digitalWrite(3,HIGH);digitalWrite(4,HIGH);digitalWrite(5,HIGH);digitalWrite(6,HIGH);digitalWrite(7,HIGH);
  delay(3000);
  lcd.clear();
}


void loop() {
  lcd.clear();
  float I = Amperemeter(Pin_Ampere);
  float V1 = Voltmeter(Pin_Volt1);

  Serial.print(I);Serial.print("\t");Serial.println(V1);
  lcd.setCursor(0,0); lcd.print("I = "); lcd.print(I); lcd.print(" mA");
  lcd.setCursor(0,1); lcd.print("V = "); lcd.print(V1); lcd.print(" V");
  delay(100);
}
