void setup()
{
  pinMode(9, OUTPUT);
  pinMode(10, OUTPUT);
  pinMode(11, OUTPUT);
}

void loop()
{
  
  digitalWrite(9, 0);
  digitalWrite(10, 1);
  digitalWrite(11, 0);
  //digitalWrite, 1);
  delay(1000);
  digitalWrite(9, 1);
  digitalWrite(10, 0);
  digitalWrite(11, 1);
  delay(1000);
  
}
