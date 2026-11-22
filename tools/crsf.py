"""
CRSF (Crossfire) — empacotamento do quadro de canais de rádio (tipo 0x16).

Formato do quadro (26 bytes no total):

    [endereço][tamanho][tipo][ ...22 bytes de canais... ][CRC]
      0xC8      24      0x16                              CRC8

- endereço: 0xC8 = "controladora de voo" (destino do quadro). Também funciona
  como byte de sincronismo: o receptor procura esse byte para achar o início.
- tamanho:  quantos bytes vêm DEPOIS dele (tipo + carga + CRC) = 1 + 22 + 1 = 24.
- tipo:     0x16 = RC_CHANNELS_PACKED (16 canais compactados).
- carga:    16 canais x 11 bits = 176 bits = 22 bytes, em little-endian.
- CRC:      CRC8 (polinômio 0xD5) calculado sobre tipo + carga.
"""

ADDR_FLIGHT_CONTROLLER = 0xC8
TYPE_RC_CHANNELS_PACKED = 0x16

NUM_CHANNELS = 16
BITS_PER_CHANNEL = 11
PAYLOAD_SIZE = NUM_CHANNELS * BITS_PER_CHANNEL // 8  # 22
FRAME_SIZE = 2 + 1 + PAYLOAD_SIZE + 1                # 26

CH_MIN = 172     # equivale a ~988 µs no Betaflight
CH_MID = 992     # ~1500 µs (centro do manche)
CH_MAX = 1811    # ~2012 µs


def pack_channels(channels: list[int]) -> bytes:
    """16 valores de 11 bits -> 22 bytes.

    Ideia: tratar a carga inteira como UM número de 176 bits.
    O canal 1 ocupa os bits 0-10, o canal 2 os bits 11-21, e assim por diante.
    Depois, convertemos esse número em 22 bytes, do menos significativo
    para o mais significativo (little-endian).
    """
    if len(channels) != NUM_CHANNELS:
        raise ValueError(f"esperava {NUM_CHANNELS} canais, recebi {len(channels)}")

    bits = 0
    for i, value in enumerate(channels):
        if not 0 <= value <= 0x7FF:          # 0x7FF = 2047, o máximo em 11 bits
            raise ValueError(f"canal {i + 1} fora de 11 bits: {value}")
        bits |= value << (i * BITS_PER_CHANNEL)

    return bits.to_bytes(PAYLOAD_SIZE, "little")


def unpack_channels(payload: bytes) -> list[int]:
    """22 bytes -> 16 valores de 11 bits (o caminho inverso)."""
    if len(payload) != PAYLOAD_SIZE:
        raise ValueError(f"carga deve ter {PAYLOAD_SIZE} bytes")

    bits = int.from_bytes(payload, "little")
    mask = (1 << BITS_PER_CHANNEL) - 1       # 0b111_1111_1111
    return [(bits >> (i * BITS_PER_CHANNEL)) & mask for i in range(NUM_CHANNELS)]


def crc8(data: bytes, poly: int = 0xD5) -> int:
    """CRC8 bit a bit, valor inicial 0, sem reflexão e sem XOR final.

    Para cada byte: misturamos no CRC (XOR) e, para cada um dos 8 bits,
    se o bit mais alto for 1, deslocamos e aplicamos o polinômio;
    se for 0, só deslocamos. O '& 0xFF' mantém o resultado em 8 bits.
    """
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = ((crc << 1) ^ poly) & 0xFF
            else:
                crc = (crc << 1) & 0xFF
    return crc


def build_frame(channels: list[int]) -> bytes:
    """Monta o quadro completo de 26 bytes."""
    payload = pack_channels(channels)
    body = bytes([TYPE_RC_CHANNELS_PACKED]) + payload     # é sobre isto que o CRC é feito
    length = len(body) + 1                                # + 1 do próprio CRC
    return bytes([ADDR_FLIGHT_CONTROLLER, length]) + body + bytes([crc8(body)])


def parse_frame(frame: bytes) -> list[int]:
    """Valida um quadro e devolve os canais. Levanta ValueError se algo estiver errado.

    Este é o "decodificador independente": depois vamos usá-lo para
    conferir o que o ESP32 manda pela serial.
    """
    if len(frame) != FRAME_SIZE:
        raise ValueError(f"quadro deve ter {FRAME_SIZE} bytes, tem {len(frame)}")
    if frame[0] != ADDR_FLIGHT_CONTROLLER:
        raise ValueError(f"endereço inesperado: 0x{frame[0]:02X}")
    if frame[1] != FRAME_SIZE - 2:
        raise ValueError(f"tamanho inesperado: {frame[1]}")
    if frame[2] != TYPE_RC_CHANNELS_PACKED:
        raise ValueError(f"tipo inesperado: 0x{frame[2]:02X}")

    body, received_crc = frame[2:-1], frame[-1]
    expected_crc = crc8(body)
    if received_crc != expected_crc:
        raise ValueError(f"CRC inválido: recebido 0x{received_crc:02X}, esperado 0x{expected_crc:02X}")

    return unpack_channels(body[1:])


if __name__ == "__main__":
    # Demonstração: manches no centro, acelerador no mínimo, resto no mínimo.
    canais = [CH_MID, CH_MID, CH_MIN, CH_MID] + [CH_MIN] * 12
    quadro = build_frame(canais)
    print("quadro:", quadro.hex(" ").upper())
    print("canais:", parse_frame(quadro))
