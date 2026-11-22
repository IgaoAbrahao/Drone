import random

import pytest

from crsf import (
    CH_MAX, CH_MID, CH_MIN, FRAME_SIZE,
    build_frame, crc8, pack_channels, parse_frame, unpack_channels,
)


@pytest.mark.parametrize("value", [CH_MIN, CH_MID, CH_MAX, 0, 0x7FF])
def test_ida_e_volta_valor_unico(value):
    canais = [value] * 16
    assert unpack_channels(pack_channels(canais)) == canais


def test_ida_e_volta_valores_misturados():
    rng = random.Random(42)  # semente fixa: o teste é sempre o mesmo
    for _ in range(1000):
        canais = [rng.randint(CH_MIN, CH_MAX) for _ in range(16)]
        assert unpack_channels(pack_channels(canais)) == canais


def test_canais_nao_se_misturam():
    # Só um canal "aceso" por vez: se houver erro de deslocamento,
    # o valor vaza para o canal vizinho e o teste mostra qual.
    for i in range(16):
        canais = [0] * 16
        canais[i] = 0x7FF
        assert unpack_channels(pack_channels(canais)) == canais


def test_carga_tem_22_bytes():
    assert len(pack_channels([CH_MID] * 16)) == 22


def test_quadro_tem_26_bytes_e_cabecalho_certo():
    quadro = build_frame([CH_MID] * 16)
    assert len(quadro) == FRAME_SIZE == 26
    assert quadro[0] == 0xC8
    assert quadro[1] == 24
    assert quadro[2] == 0x16


def test_crc_de_dados_vazios_e_zero():
    assert crc8(b"") == 0


def test_alterar_um_byte_quebra_o_crc():
    quadro = bytearray(build_frame([CH_MID] * 16))
    # Começa em 3: o byte 2 (tipo) também entra no CRC, mas o parse_frame
    # rejeita um tipo errado antes de chegar a checar o CRC.
    for pos in range(3, FRAME_SIZE - 1):     # cada byte da carga
        corrompido = bytearray(quadro)
        corrompido[pos] ^= 0x01               # inverte 1 bit
        with pytest.raises(ValueError, match="CRC"):
            parse_frame(bytes(corrompido))


def test_parse_devolve_os_canais():
    canais = list(range(CH_MIN, CH_MIN + 16 * 100, 100))
    assert parse_frame(build_frame(canais)) == canais


def test_rejeita_valor_fora_de_11_bits():
    with pytest.raises(ValueError):
        pack_channels([2048] + [CH_MID] * 15)


def test_rejeita_quantidade_errada_de_canais():
    with pytest.raises(ValueError):
        pack_channels([CH_MID] * 15)
