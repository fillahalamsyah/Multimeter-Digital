#include <Adafruit_LiquidCrystal.h>
Adafruit_LiquidCrystal lcd(0);

int AM = A0; // Amperemeter
int VM = A1; // Voltmeter
int OM = A2; // Ohmmeter

void setup()
{
  pinMode(AM,INPUT);
  pinMode(VM,INPUT);
  pinMode(OM,INPUT);
  
  Serial.begin(9600);
  Serial.println("AVOMETER (Multimeter Digital)");
  lcd.begin(16, 2);
  lcd.setCursor(4,0);
  lcd.print("AVOMETER");
  lcd.setCursor(3,1);
  lcd.print("MULTIMETER");
}

float Amperemeter(){
  float RA = 1000;				// Resistor Sensor Amperemeter
  float ADC_I = analogRead(AM); // Baca nilai analog
  float VadcI = 5*ADC_I/1023; 	// Voltase ADC
  float I_ukur = VadcI/RA; 		// Arus dalam ampere
  float I_mili = I_ukur * 1000; // diubah ke mA
  return I_mili;
}
float Voltmeter(){
  float RV1 = 1000;			// Resistor 1 Voltmeter
  float RV2 = 1000;				// Resistor 2 Voltmeter
  float ADC_V = analogRead(VM);	// Baca nilai analog 
  float VadcV = 5*ADC_V/1023;	// Voltase ADC
  float V_ukur = VadcV*(RV1+RV2)/RV2;// Tegangan terukur
  return V_ukur;
}

float Ohmmeter(){
  float Vcc = 5;				// Tegangan VCC
  float RO = 1000;				// Resistor Sensor Ohmmeter
  float ADC_O = analogRead(OM);	// Baca nilai Analog
  float VadcO = 5*ADC_O/1023;	// Voltase AdC
  float buffer =(Vcc/VadcO - 1);// Tegangan Buffer
  float R_uji = RO/buffer;		// Hambatan Resistor Uji
  return R_uji;
}

void loop(){
  float I_mili = Amperemeter();
  float V_ukur = Voltmeter();
  float R_uji = Ohmmeter();
  
  //Kontrol Serial Monitor
  if (Serial.available()>0){
    int baca = Serial.read();
    if (baca == 'a'){
      lcd.clear();
      lcd.setCursor(2,0);
      lcd.print("Amperemeter");
      lcd.setCursor(0,1);
      lcd.print(I_mili);
      lcd.print(" mA");
      
      Serial.println("-----Amperemeter-----");
      Serial.print("Arus = ");
      Serial.print(I_mili);
      Serial.println(" mA");
      
      
    }else if (baca == 'v'){
      lcd.clear();
      lcd.setCursor(4,0);
      lcd.print("Voltmeter");
      lcd.setCursor(0,1);
      lcd.print(V_ukur);
      lcd.print(" Volt");
      
      Serial.println("-----Voltmeter-----");
      Serial.print("Tegangan = ");
      Serial.print(V_ukur);
      Serial.println(" Volt");
      
    }else if (baca == 'o'){
      lcd.clear();
      lcd.setCursor(4,0);
      lcd.print("Ohmmeter");
      lcd.setCursor(0,1);
      lcd.print(R_uji);
      lcd.print(" Ohm");
      
      Serial.println("-----Ohmmeter-----");
      Serial.print("Resistansi = ");
      Serial.print(R_uji);
      Serial.println(" Ohm");
      
    }else if (baca == 's'){
      lcd.clear();
      lcd.setCursor(4,0);
      lcd.print("SELESAI");
      Serial.println("-----SELESAI-----");
      //while(1);
    }
  }
}
