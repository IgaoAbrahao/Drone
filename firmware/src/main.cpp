#include <Arduino.h>

// LED azul embutido na maioria dos ESP32 DevKit V1 (GPIO2).
constexpr uint8_t PINO_LED = 2;

void setup() {
  // Abre a serial USB. O valor TEM de ser igual ao monitor_speed do
  // platformio.ini; senão o monitor mostra caracteres sem sentido.
  Serial.begin(115200);
  pinMode(PINO_LED, OUTPUT);

  delay(500);  // dá tempo para o monitor serial conectar antes da 1a mensagem
  Serial.println();
  Serial.println("ESP32 pronto");
  Serial.printf("Chip: %s, %u MHz, %u nucleos\n",
                ESP.getChipModel(), ESP.getCpuFreqMHz(), ESP.getChipCores());
}

void loop() {
  static uint32_t contador = 0;  // static: mantém o valor entre as voltas do loop

  digitalWrite(PINO_LED, HIGH);
  delay(500);
  digitalWrite(PINO_LED, LOW);
  delay(500);

  Serial.printf("contador = %u\n", contador++);
}