#include <Servo.h>

#define SERIAL_SPEED 38400
#define START_BYTE 'a'
#define MSG_LEN 5

char r[MSG_LEN];
char started = 0;
char cur_len = 0;
char in;
Servo s[3];

void setup()
{
  Serial.begin(SERIAL_SPEED);
  s[0].attach(9);
  s[1].attach(10);
  s[2].attach(11);
}

int checksum(char* c)
{
  return 1;
}

void loop()
{
  
  while (Serial.available() > 0) {
    in = Serial.read();
    if(!started && in != START_BYTE) continue;
    started = 1;
    r[cur_len] = in;
    cur_len++;
    if(cur_len == MSG_LEN)
    {
      started = false;
      cur_len = 0;
      if(checksum(r) > 0)
      {
        s[0].write((unsigned char)r[1]);
        s[1].write((unsigned char)r[2]);
        s[2].write((unsigned char)r[3]);
      }
    }
    
  }
}
