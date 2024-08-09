int Pin_Ampere = A0; // Pin Analog Input Amperemeter
int Pin_Volt1 = A1; // Pin Analog Input Voltmeter 1
int Pin_Volt2 = A2; // Pin Analog Input Voltmeter 2
int Pin_Ohm = A3; // Pin Analog Input Ohmmeter

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

// Fungsi untuk membaca nilai hambatan pada rangkaian Ohmmeter
float Ohmmeter(int Pin){
  float Vcc = 5;        // Tegangan VCC
  float RO = 1000;        // Resistor Sensor Ohmmeter 1k
  float ADC_O = analogRead(Pin);  // Baca nilai Analog
  float VadcO = 5*ADC_O/1023;  // Voltase AdC
  float buffer =(Vcc/VadcO - 1);// Tegangan Buffer
  float R_uji = RO/buffer;    // Hambatan Resistor Uji (Ohm)
  return R_uji;
}

void setup() {
  Serial.begin(9600);
  pinMode(Pin_Ampere,INPUT);
  pinMode(Pin_Volt1,INPUT);
  pinMode(Pin_Volt2,INPUT);
  pinMode(Pin_Ohm,INPUT);

}

void loop() {
  // Hasil print akan seperti berikut :
  // A    V     O
  // 1.0  1.0   1.0
  // Setiap nilai dipisahkan oleh tab "\t"
  // Dapat diganti dengan Koma "," atau Titik Koma ";"
  float I = Amperemeter(Pin_Ampere);
  float V1 = Voltmeter(Pin_Volt1);
  float V2 = Voltmeter(Pin_Volt2);
  float R = Ohmmeter(Pin_Ohm);
  Serial.print(I);
  Serial.print("\t"); //Pemisah untuk pembacaan Python
  Serial.print(V1);
  Serial.print("\t"); //Pemisah untuk pembacaan Python
  Serial.print(V2);
  Serial.print("\t"); //Pemisah untuk pembacaan Python
  Serial.println(R);
}
