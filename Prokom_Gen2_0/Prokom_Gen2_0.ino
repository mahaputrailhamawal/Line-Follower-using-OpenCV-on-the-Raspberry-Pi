//================================= Include Library ==================================//
#include <stdio.h>
#include <stdlib.h>

#define LEFT 0
#define RIGHT 1

//================================= Variabel Global ==================================//
float PWM_MOTORKANAN,PWM_MOTORKIRI;
String ARAH_MOTOR;
String dataIn;
String BUFF[100];
boolean parsing=false;
int i;

//Standard PWM DC control
int E1 = 5;     //M1 Speed Control
int E2 = 6;     //M2 Speed Control
int M1 = 4;    //M1 Direction Control
int M2 = 7;    //M1 Direction Control

//================================= Deklarasi Fungsi ==================================//
void kirimData();
void parsingData();
void modeBehenti();
void modeMaju(float PWM_MOTORKIRI, float PWM_MOTORKANAN);
void modeMundur(float PWM_MOTORKIRI, float PWM_MOTORKANAN); 
void modeBelokKiri(float PWM_MOTORKIRI, float PWM_MOTORKANAN);
void modeBelokKanan(float PWM_MOTORKIRI, float PWM_MOTORKANAN);
void LwheelSpeed();
void RwheelSpeed();
//================================== Main Program ====================================//
void setup() {
   Serial.begin(9600);
   for(i=4;i<=7;i++)
     pinMode(i, OUTPUT);   
   dataIn="";
}

void loop() {
  if(Serial.available()>0) {
    char inChar = (char)Serial.read();
    dataIn += inChar;
    if (inChar == 'q') {
    parsing = true;
  }
  
}
 
if(parsing){
    parsingData();
    parsing=false;
    dataIn="";
  }
    Control();
    //kirimData();
}

//=====================================================================================//

//=============================Deklrasi Fungsi========================================//
void modeBerhenti(void)                    //berhenti
{
  digitalWrite(E1,LOW);   
  digitalWrite(E2,LOW);      
}   
void modeMaju(float PWM_MOTORKIRI, float PWM_MOTORKANAN)                //maju 
{
  analogWrite (E1,PWM_MOTORKIRI);                     //PWM Speed Control
  digitalWrite(M1,HIGH);    
  analogWrite (E2,PWM_MOTORKANAN);    
  digitalWrite(M2,HIGH);
}  
void modeMundur(float PWM_MOTORKIRI, float PWM_MOTORKANAN)             //mundur
{
  analogWrite (E1,PWM_MOTORKIRI);
  digitalWrite(M1,LOW);   
  analogWrite (E2,PWM_MOTORKANAN);    
  digitalWrite(M2,LOW);
}
void modeBelokKiri(float PWM_MOTORKIRI, float PWM_MOTORKANAN)           //belok kiri
{
  analogWrite (E1,PWM_MOTORKIRI);
  digitalWrite(M1,LOW);    
  analogWrite (E2,PWM_MOTORKANAN);    
  digitalWrite(M2,HIGH);
}
void modeBelokKanan(float PWM_MOTORKIRI, float PWM_MOTORKANAN)            //belok kanan
{
  analogWrite (E1,PWM_MOTORKIRI);
  digitalWrite(M1,HIGH);    
  analogWrite (E2,PWM_MOTORKANAN);    
  digitalWrite(M2,LOW);
}

void Control(){
  if (ARAH_MOTOR == "maju")
  {
    modeMaju(PWM_MOTORKIRI,PWM_MOTORKANAN); 
  }
  else if(ARAH_MOTOR == "mundur")
  {
    modeMundur(PWM_MOTORKIRI,PWM_MOTORKANAN); 
  }
  else if(ARAH_MOTOR == "kana")
  {
    modeBelokKanan(PWM_MOTORKIRI,PWM_MOTORKANAN);
  }
  else if(ARAH_MOTOR == "kiri")
  {
    modeBelokKiri(PWM_MOTORKIRI,PWM_MOTORKANAN);
  }
  else if(ARAH_MOTOR == "stop")
  {
    modeBerhenti();
  }
}
void kirimData(){
    Serial.print("#");
    Serial.print(ARAH_MOTOR);
    Serial.print("#");
    Serial.print(PWM_MOTORKIRI);
    Serial.print("#");
    Serial.print(PWM_MOTORKANAN);
    Serial.print("#");
    Serial.print("\n");
}

void parsingData(){
  int j=0;
  BUFF[j]="";
  
  for(i=1;i<dataIn.length();i++){
    if ((dataIn[i] == '#') || (dataIn[i] == ','))
      {
        j++;
        BUFF[j]="";       //inisialisasi variabel array BUFF[j]
      }
    else
      BUFF[j] = BUFF[j] + dataIn[i];
  } 
   
   ARAH_MOTOR         = BUFF[0].c_str();
   PWM_MOTORKIRI      = atof(BUFF[1].c_str());
   PWM_MOTORKANAN     = atof(BUFF[2].c_str());
}
