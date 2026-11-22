# drone-radio

Projeto de aprendizado: rádio controle (ESP32 + CRSF + ELRS) e drone sub-250 g, feitos do zero.
O contexto completo e as decisões estão em docs/contexto-drone.md. Leia antes de começar.

## Como trabalhar
- Responda em português.
- Você pode escrever o código, mas sempre bem comentado, explicando o porquê de cada parte.
- Cada entrega termina com 2 ou 3 desafios curtos: prever uma saída, quebrar e consertar, ou fazer uma pequena alteração. O objetivo é eu entender, não só ter código funcionando.
- Não use bibliotecas CRSF prontas. Referências: especificação CRSF da TBS e código-fonte do ExpressLRS.
- Rode os testes (pytest em tools/) antes de dizer que algo está pronto.
- Quando uma decisão nova for tomada, atualize docs/contexto-drone.md.

## Estrutura
- tools/      Python: crsf.py (empacotador e decodificador) e testes
- firmware/   PlatformIO, ESP32 (framework Arduino)
- docs/       contexto e tabela de canais

## Segurança
Testes com motores sempre sem hélices. Armar só com acelerador em zero.
