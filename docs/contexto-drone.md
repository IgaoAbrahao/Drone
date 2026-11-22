# Projeto Drone DIY — Contexto e decisões

## Objetivo
Construir um drone do zero, abaixo de 250 g, para filmar, com um rádio controle com tela também construído do zero. Foco em APRENDER os protocolos, não em "vibe code".

## Regras de trabalho
- O Claude escreve o código, bem comentado, explicando o porquê de cada parte.
- Cada entrega vem com perguntas e desafios curtos (prever saídas, quebrar e consertar, pequenas alterações), para o Igor entender de verdade e não virar vibe code.
- Validar sempre em camadas, comparando com algo conhecido (testes, decodificador independente, analisador lógico).

## Arquitetura decidida
- **Drone:** cinewhoop 3" com proteção de hélice, controladora F405 + ESC 4 em 1 (Betaflight), motores 1404/1505, bateria 4S 650–850 mAh, receptor ELRS. Peso alvo: 200–240 g com câmera.
- **Câmera:** câmera de ação leve gravando a bordo (Insta360 GO 3 ou GoPro naked). Se quiser gravar/parar pelo rádio, escolher câmera que aceite acionamento por fio (GoPro naked, RunCam Thumb).
- **Vídeo ao vivo:** transmissor 5,8 GHz (analógico, mais barato; ou digital Walksnail/HDZero, mais caro). A decidir.
- **Controle (rádio):** construído pelo Igor. ESP32 lê manches e chaves → gera quadros CRSF → módulo ELRS TX (2,4 GHz). Tela para telemetria.
- Descartado: controle pelo iPhone (alcance de Wi-Fi curto). Gimbal estabilizado (peso).
- Regulação Brasil: voo sempre à vista (VLOS); abaixo de 250 g as exigências são menores.

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

Tela: tensão da bateria do drone, LQ/RSSI, armado/desarmado, modo de voo, cronômetro, bateria do rádio.
Segurança: só armar com acelerador em zero; alerta de bateria baixa; failsafe configurado; testes sempre SEM hélices.

## Etapas de aprendizado
1. Manches: ADC, calibração (mín/centro/máx), zona morta, expo. ← foco atual (só manches; chaves, botões e potenciômetros depois)
2. CRSF: quadro serial 420000 baud, 16 canais de 11 bits, CRC8.
3. Link ELRS no ar (estudar, não reimplementar).
4. Receptor → controladora: CRSF, MSP, telemetria.
5. Vídeo.

## Hardware comprado (etapa 1–3)
ESP32 DevKit V1 30 pinos (x2), 2 joysticks KY-023, protoboard 830, jumpers, cabo USB de dados, adaptador USB-C, conversor USB-serial CP2102 (3,3 V), analisador lógico 24 MHz 8 canais, multímetro.
Comprar depois (quando o software dos manches estiver pronto): potenciômetros B10K, chave ON-ON, chave ON-OFF-ON, botões 6x6. Peças definitivas (gimbals hall etc.) só junto com o projeto da carcaça impressa.

## Ligações
- Joysticks em 3V3 (nunca 5 V). J1: VRx→GPIO34, VRy→GPIO35. J2: VRx→GPIO32, VRy→GPIO33 (ADC1, funciona com Wi-Fi ligado).
- Potenciômetro futuro: GPIO36 ou GPIO39. Chaves/botões: GPIO digital com pull-up interno.
- Teste CRSF: GPIO17 (TX2) → RX do conversor USB-serial; GNDs unidos; NÃO ligar VCC do conversor. Começar a 115200 e depois subir para 420000 (taxa não padrão, pode dar problema no macOS).

## Ambiente
- MacBook. VS Code + PlatformIO (framework Arduino). Python 3 em venv + pyserial + pytest. PulseView para o analisador lógico.
- Não usar bibliotecas CRSF prontas. Referências: especificação CRSF da TBS e código-fonte do ExpressLRS (GitHub).
- Repositório: drone-radio/ com README.md, docs/canais.md, tools/ (crsf.py, test_crsf.py), firmware/ (PlatformIO).

## Estado atual
Próximos passos do Igor (antes de rodar qualquer código):
1. Criar o venv e instalar pyserial + pytest.
2. Levar este contexto para o Projeto no Claude.
3. Configurar o Claude Code no repositório (com CLAUDE.md).

Já entregue pelo Claude (ainda não rodado pelo Igor): tools/crsf.py e tools/test_crsf.py (14 testes passando).
- crsf.py: pack_channels, unpack_channels, crc8 (poli 0xD5, início 0), build_frame, parse_frame (decodificador independente que valida endereço, tamanho, tipo e CRC).
- Formato: [0xC8] [24] [0x16] [22 bytes] [CRC] = 26 bytes. CRC sobre tipo + carga. Canais 172/992/1811, little-endian (canal 1 nos bits 0–10).
- Lição já aparecida: corromper o byte de tipo falha na checagem de tipo antes do CRC; a ordem das validações importa.

Desafios pendentes do Igor:
1. Explicar à mão por que, com canais 1 e 2 em 992, a carga começa com E0 03 1F.
2. Trocar "little" por "big" só no pack_channels e prever quais testes falham.
3. Trocar o polinômio para 0xD4: os testes passam? O que isso diz sobre o que os testes provam e o que só o Betaflight vai provar?

Depois: firmware do ESP32 lendo os manches (ADC, calibração, zona morta).
