#include <Arduino.h>

// ---------------------------------------------------------------------------
// Leitura bruta dos 2 joysticks (4 eixos) pelo ADC1 do ESP32.
//
// Objetivo desta versão: só MEDIR e MOSTRAR os números reais na serial, para
// descobrirmos o mínimo, o centro e o máximo de cada eixo. A conversão para
// 172–1811 (CRSF) vem depois, usando esses números.
//
// Ligação (joysticks SEMPRE em 3V3, nunca em 5V: os pinos do ESP32 não
// suportam 5V e podem queimar):
//   J1: VRx -> GPIO34, VRy -> GPIO35
//   J2: VRx -> GPIO32, VRy -> GPIO33
//   VCC dos dois -> 3V3, GND dos dois -> GND
// ---------------------------------------------------------------------------

constexpr uint8_t NUM_EIXOS = 4;

// Só usamos pinos do ADC1. O ADC2 do ESP32 não funciona quando o Wi-Fi está
// ligado, e queremos poder usar o Wi-Fi no futuro sem refazer a ligação.
constexpr uint8_t PINOS[NUM_EIXOS] = {34, 35, 32, 33};
const char* const NOMES[NUM_EIXOS] = {"J1x", "J1y", "J2x", "J2y"};

// O ADC do ESP32 tem ruído: a mesma posição do manche dá leituras que variam
// alguns pontos. Tirar a média de várias leituras seguidas deixa o número
// estável, sem custar quase nada de tempo.
constexpr uint8_t AMOSTRAS = 16;

// Intervalo entre impressões na serial (ms).
constexpr uint32_t INTERVALO_MS = 100;

// Menor e maior valor visto em cada eixo desde que o programa começou.
// Movendo os manches até os extremos, estes números viram a calibração.
int minimo[NUM_EIXOS];
int maximo[NUM_EIXOS];

// Lê um eixo: média de AMOSTRAS leituras. Devolve 0..4095 (ADC de 12 bits).
int lerEixo(uint8_t pino) {
  uint32_t soma = 0;
  for (uint8_t i = 0; i < AMOSTRAS; i++) {
    soma += analogRead(pino);
  }
  return soma / AMOSTRAS;
}

void setup() {
  // Mesma velocidade do monitor_speed no platformio.ini.
  Serial.begin(115200);

  // 12 bits = valores de 0 a 4095.
  analogReadResolution(12);
  // 11 dB de atenuação: o ADC passa a medir até perto de 3,3 V. Sem isso a
  // faixa seria bem menor e o manche saturaria antes do fim do curso.
  analogSetAttenuation(ADC_11db);

  // Começam "ao contrário" para que a primeira leitura real já sobrescreva.
  for (uint8_t i = 0; i < NUM_EIXOS; i++) {
    minimo[i] = 4095;
    maximo[i] = 0;
  }

  delay(500);  // dá tempo para o monitor serial conectar
  Serial.println();
  Serial.println("ESP32 pronto");
    // %lu + conversão para unsigned long: forma portátil de imprimir um uint32_t
  Serial.printf("Chip: %s, %lu MHz, %u nucleos\n",
                ESP.getChipModel(), (unsigned long)ESP.getCpuFreqMHz(), ESP.getChipCores());
  Serial.println("Mexa os manches: deixe parados, depois leve aos extremos.");
}

void loop() {
  // millis() em vez de delay(): o loop continua livre para outras tarefas
  // (mais tarde, mandar o quadro CRSF em intervalo fixo).
  static uint32_t ultimo = 0;
  if (millis() - ultimo < INTERVALO_MS) {
    return;
  }
  ultimo = millis();

  for (uint8_t i = 0; i < NUM_EIXOS; i++) {
    int valor = lerEixo(PINOS[i]);
    if (valor < minimo[i]) minimo[i] = valor;
    if (valor > maximo[i]) maximo[i] = valor;
    Serial.printf("%s=%4d (min %4d max %4d)  ", NOMES[i], valor, minimo[i], maximo[i]);
  }
  Serial.println();
}