#include <SPI.h>
#include <Ethernet.h>
#include <EthernetUdp.h>

// Конфигурация сети для Arduino (измените под вашу сеть)
byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
IPAddress ip(192.168.1.50);
unsigned int localPort = 8888;

char packetBuffer[UDP_TX_PACKET_MAX_SIZE];
EthernetUDP Udp;

void setup() {
  Ethernet.begin(mac, ip);
  Udp.begin(localPort);
  
  // Настройка встроенного светодиода для теста команды
  pinMode(LED_BUILTIN, OUTPUT); 
}

void loop() {
  int packetSize = Udp.parsePacket();
  if (packetSize) {
    Udp.read(packetBuffer, UDP_TX_PACKET_MAX_SIZE);
    String command = String(packetBuffer).substring(0, packetSize);
    
    if (command == "ON") {
      digitalWrite(LED_BUILTIN, HIGH);
      // Здесь добавляется код для открытия руки (натяжение кабелей)
    } else if (command == "OFF") {
      digitalWrite(LED_BUILTIN, LOW);
      // Здесь добавляется код для закрытия руки (ослабление кабелей)
    }
    memset(packetBuffer, 0, sizeof(packetBuffer));
  }
  delay(10);
}
