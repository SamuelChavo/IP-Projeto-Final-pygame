TAMANHO = 10
TOTAL_NAVIOS = 7
TAMANHO_NAVIO = 3

VAZIO = 0
NAVIO = 1
ACERTO = 2
ERRO = 3


def criar_tabuleiro():
    tabuleiro = []
    for i in range(TAMANHO):
        linha = []
        for j in range(TAMANHO):
            linha.append(VAZIO)
        tabuleiro.append(linha)
    return tabuleiro


def posicionar_navio(tabuleiro, linha, coluna):
    if coluna + TAMANHO_NAVIO > TAMANHO:
        return False

    for c in range(coluna, coluna + TAMANHO_NAVIO):
        if tabuleiro[linha][c] != VAZIO:
            return False

    for c in range(coluna, coluna + TAMANHO_NAVIO):
        tabuleiro[linha][c] = NAVIO

    return True


def contar_navios(tabuleiro):
    count = 0
    for linha in tabuleiro:
        for celula in linha:
            if celula == NAVIO:
                count += 1
    return count


def navios_posicionados(tabuleiro):
    return contar_navios(tabuleiro) == TOTAL_NAVIOS * TAMANHO_NAVIO


def encontrar_navio(tabuleiro, linha, coluna):
    celulas = []
    c = coluna
    while c >= 0 and tabuleiro[linha][c] == NAVIO:
        c -= 1
    c += 1
    while c < TAMANHO and tabuleiro[linha][c] == NAVIO:
        celulas.append((linha, c))
        c += 1
    return celulas


def atacar(tabuleiro, linha, coluna):
    celula = tabuleiro[linha][coluna]

    if celula == ACERTO or celula == ERRO:
        return "ja_atacado"

    if celula == NAVIO:
        partes = encontrar_navio(tabuleiro, linha, coluna)
        for (l, c) in partes:
            tabuleiro[l][c] = ACERTO
        return "acerto"

    tabuleiro[linha][coluna] = ERRO
    return "erro"


def todos_navios_destruidos(tabuleiro):
    for linha in tabuleiro:
        for celula in linha:
            if celula == NAVIO:
                return False
    return True