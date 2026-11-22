# Projeto Drone DIY — Contexto e decisões

## Objetivo
Construir um drone do zero, abaixo de 250 g, para filmar, com um rádio controle com tela também construído do zero. Foco em ENTENDER os protocolos conversando; a implementação é feita pelo Claude (decisão do Igor em 22/11/2026, ver "Regras de trabalho").

## Regras de trabalho
- Fluxo decidido pelo Igor em 22/11/2026: primeiro DISCUTIR a etapa/protocolo, depois o Claude IMPLEMENTA. O Igor aceita que a implementação seja "vibe code"; o contexto deste documento é o que mantém o Claude no trilho.
- O Claude escreve o código, bem comentado, explicando o porquê de cada parte.
- Sem desafios/exercícios por padrão; só quando o Igor pedir. (As instruções do Projeto ainda mencionam desafios: o Igor pode editá-las se quiser que isso valha sempre.)
- Validar sempre em camadas, comparando com algo conhecido (decodificador independente, vetores calculados à mão, projetos DIY abertos como gabarito, analisador lógico).
- Testes em Python: o Igor os considera de pouco valor. Ver "Estado atual".

## Arquitetura decidida
- **Drone:** cinewhoop 3" com proteção de hélice, controladora F405 + ESC 4 em 1 (Betaflight), motores 1404/1505, bateria 4S 650–850 mAh, receptor ELRS. Peso alvo: 200–240 g com câmera.
- **Câmera:** câmera de ação leve gravando a bordo (Insta360 GO 3 ou GoPro naked). Se quiser gravar/parar pelo rádio, escolher câmera que aceite acionamento por fio (GoPro naked, RunCam Thumb).
- **Vídeo ao vivo:** transmissor 5,8 GHz (analógico, mais barato; ou digital Walksnail/HDZero, mais caro). A decidir.
- **Controle (rádio):** construído pelo Igor. ESP32 lê manches e chaves → gera quadros CRSF → módulo ELRS TX (2,4 GHz). Tela para telemetria.
- Descartado: controle pelo iPhone (alcance de Wi-Fi curto). Gimbal estabilizado (peso).
- Regulação Brasil: voo sempre à vista (VLOS); abaixo de 250 g as exigências são menores.

## Cadeia de comunicação (entendida em 22/11/2026)
manches (analógico) → ESP32 (ADC 0–4095 → 172–1811) → CRSF por fio → módulo ELRS TX → ar (formato próprio do ELRS, não reimplementar) → receptor ELRS → CRSF por fio → Betaflight.
- Cada salto digital tem o seu CRC; pacote ruim é descartado, sem retransmissão (dado velho não serve). Perda prolongada → failsafe da controladora.
- O quadro é enviado continuamente (dezenas a centenas de vezes por segundo), com o manche parado ou não.
- **Endereço do quadro:** 0xC8 = controladora de voo (lado receptor → controladora). No lado rádio → módulo TX o EdgeTX usa 0xEE (módulo transmissor). O CRC cobre só tipo + carga, então trocar o endereço não muda o CRC.
- **Velocidade da serial:** receptor → controladora ~420000 baud. Rádio → módulo TX: 400000 ou 115200 (o módulo detecta sozinho). Para o ESP32 → módulo, usar 400000 (ou 115200 no primeiro teste), NÃO 420000.

## Tabela de canais (versão 1)
| Canal | Função | Comando físico |
|---|---|---|
| 1 a 4 | Rolagem, arfagem, aceleração, guinada | 2 manches |
| 5 | Armar/desarmar | chave 2 posições, com trava |
| 6 | Modo de voo (Angle/Horizon/Acro) | chave 3 posições |
| 7 | Bipe para achar o drone | botão |
| 8 | Modo tartaruga | chave |
| 9 | Inclinação da câmera (servo) | potenciômetro |
| 10 | Gravar/parar | botão (se a câmera permitir) |

Valores: manche no centro = 992; todo à esquerda/embaixo = 172; todo à direita/em cima = 1811 (proporcional no meio). Acelerador não volta ao centro (fica onde for deixado).
Tela: tensão da bateria do drone, LQ/RSSI, armado/desarmado, modo de voo, cronômetro, bateria do rádio.
Segurança: só armar com acelerador em zero; alerta de bateria baixa; failsafe configurado; testes sempre SEM hélices.

## Etapas
1. Manches: ADC, calibração (mín/centro/máx), zona morta, expo. ← foco atual (só manches; chaves, botões e potenciômetros depois)
2. CRSF no ESP32: quadro serial, 16 canais de 11 bits, CRC8 (endereço 0xEE e 400000 baud para o módulo TX).
3. Link ELRS no ar (estudar, não reimplementar).
4. Receptor → controladora: CRSF, MSP, telemetria.
5. Vídeo.

## Hardware comprado (etapa 1–3)
ESP32 DevKit V1 30 pinos (x2), 2 joysticks KY-023, protoboard 830, jumpers, cabo USB de dados, adaptador USB-C, conversor USB-serial CP2102 (3,3 V), analisador lógico 24 MHz 8 canais, multímetro.
Ainda NÃO comprados: módulo ELRS TX e receptor ELRS. Antes de comprar o módulo, checar no datasheet se a ligação com o rádio usa um fio só (half-duplex) ou dois (TX e RX).
Comprar depois (quando o software dos manches estiver pronto): potenciômetros B10K, chave ON-ON, chave ON-OFF-ON, botões 6x6. Peças definitivas (gimbals hall etc.) só junto com o projeto da carcaça impressa.
Obs.: os KY-023 voltam sozinhos ao centro, inclusive no eixo do acelerador; serve para teste, mas no rádio final o acelerador não pode ter mola de retorno.

## Ligações
- Joysticks em 3V3 (nunca 5 V). J1: VRx→GPIO34, VRy→GPIO35. J2: VRx→GPIO32, VRy→GPIO33 (ADC1, funciona com Wi-Fi ligado).
- Potenciômetro futuro: GPIO36 ou GPIO39. Chaves/botões: GPIO digital com pull-up interno.
- Teste CRSF: GPIO17 (TX2) → RX do conversor USB-serial; GNDs unidos; NÃO ligar VCC do conversor. Começar a 115200 e depois subir para 400000 (taxa não padrão, pode dar problema no macOS).

## Ambiente
- MacBook. VS Code + PlatformIO (framework Arduino). Python 3 em venv + pyserial + pytest. PulseView para o analisador lógico.
- Bibliotecas: usar à vontade para o que não é o ponto (tela, filtros, utilitários). Para CRSF não existe biblioteca pronta para o lado do RÁDIO (as encontradas são do lado receptor); o quadro será escrito em C++ no ESP32. Gabarito para comparar: projetos DIY abertos de rádio ELRS, como Arduino-Transmitter-for-ELRS (kkbin505) e repositórios de "ESP32 ELRS handset" (ainda não lidos). Outras referências: especificação CRSF (TBS / crsf-wg) e código-fonte do ExpressLRS.
- Repositório: drone-radio/ com README.md, docs/canais.md, tools/ (crsf.py, test_crsf.py), firmware/ (PlatformIO).

## Estado atual
tools/crsf.py e tools/test_crsf.py existem (14 testes). Em 22/11/2026 foram rodados e verificados pelo Claude:
- crsf.py: pack_channels, unpack_channels, crc8 (poli 0xD5, início 0, sem reflexão, sem XOR final), build_frame, parse_frame (valida endereço, tamanho, tipo e CRC). Tem demonstração em `python crsf.py`.
- Formato: [endereço] [24] [0x16] [22 bytes] [CRC] = 26 bytes. CRC sobre tipo + carga. Canais 172/992/1811, little-endian.
- Empacotamento = "fila de bits": o canal i ocupa os bits 11·i a 11·i+10 de um inteiro de 176 bits, convertido em 22 bytes little-endian. 8 canais = 88 bits = 11 bytes exatos, então o padrão se repete a cada 8 canais.
- Verificação independente: com os 16 canais em 992, a carga começa com E0 03 1F F8 C0 07 (calculado à mão pelo Igor e confere com o código). crc8("123456789") = 0xBC, o valor de verificação padrão do CRC-8/DVB-S2.
- Quadro de referência (endereço 0xC8, tudo em 992): C8 18 16 E0 03 1F F8 C0 07 3E F0 81 0F 7C E0 03 1F F8 C0 07 3E F0 81 0F 7C AD
- Limite dos 14 testes: são quase todos de ida e volta e passam mesmo com o polinômio errado (0xD4) ou com "big" trocado nos dois lados. Foram propostos 2 testes que pegam esses erros (bytes calculados à mão e crc8 = 0xBC), ainda NÃO adicionados ao arquivo.
- Papel do crsf.py daqui para frente: "régua" para decodificar as capturas do ESP32 (o Igor cola os bytes, o Claude decodifica). Ajuste pendente: parse_frame precisa aceitar o endereço 0xEE (hoje só aceita 0xC8) e o endereço deve virar parâmetro.
- Lição: corromper o byte de tipo falha na checagem de tipo antes do CRC; a ordem das validações importa.

Próximo passo: discutir e depois implementar o firmware do ESP32 lendo os manches (ADC, calibração, zona morta, conversão para 172–1811).