# drone-radio

Projeto: rádio controle (ESP32 + CRSF + ELRS) e drone sub-250 g, feitos do zero.
O contexto completo e as decisões estão em docs/contexto-drone.md. Leia antes de começar.

## Como trabalhar
- Responda em português.
- Fluxo: primeiro discutimos a etapa ou o protocolo, depois você implementa. Não comece a escrever código antes de eu confirmar as decisões em aberto.
- Escreva código bem comentado, explicando o porquê de cada parte.
- Não termine entregas com desafios ou exercícios, a menos que eu peça.
- CRSF: não existe biblioteca pronta para o lado do rádio. Escreva o quadro em C++ no ESP32. Para o resto (tela, filtros, utilitários), pode usar bibliotecas.
- Referências: especificação CRSF (TBS / crsf-wg) e código-fonte do ExpressLRS. Projetos DIY abertos de rádio ELRS servem de gabarito.
- Valide em camadas, comparando com algo conhecido: vetor calculado à mão, tools/crsf.py como decodificador, analisador lógico. Antes de dizer que algo está pronto, mostre a evidência (bytes, saída), não só "deve funcionar".
- Ao mexer em tools/crsf.py, rode o pytest em tools/.
- Quando uma decisão nova for tomada, atualize docs/contexto-drone.md e me avise que a cópia do Projeto no claude.ai também precisa ser atualizada.

## Estrutura
- tools/      Python: crsf.py (empacotador e decodificador) e testes
- firmware/   PlatformIO, ESP32 (framework Arduino)
- docs/       contexto e tabela de canais

## Segurança
Testes com motores sempre sem hélices. Armar só com acelerador em zero.