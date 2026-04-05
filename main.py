import pygame
import sys
import logic

pygame.init()

LARGURA = 700
ALTURA = 750
TAMANHO_CELULA = 52
MARGEM = 2
OFFSET_X = 35
OFFSET_Y = 130

COR_FUNDO      = (15,  25,  50)
COR_AGUA       = (30,  80, 160)
COR_AGUA_HOVER = (50, 110, 200)
COR_GRADE      = (20,  50, 110)
COR_NAVIO      = (80, 180,  80)
COR_ACERTO     = (220,  60,  60)
COR_ERRO       = (180, 180, 220)
COR_TEXTO      = (240, 240, 255)
COR_AVISO      = (255, 200,  50)
COR_VITORIA    = (80,  220, 120)
COR_BOTAO      = (40,  90, 180)
COR_BOTAO_H    = (60, 120, 220)
COR_OVERLAY    = (10,  18,  40, 210)

FONTE_GRANDE = pygame.font.SysFont("segoeui", 28, bold=True)
FONTE_MEDIA  = pygame.font.SysFont("segoeui", 20)
FONTE_PEQUENA= pygame.font.SysFont("segoeui", 15)

tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Batalha Naval")
relogio = pygame.time.Clock()

FASE_POSICIONAR = "posicionar"
FASE_TRANSICAO  = "transicao"
FASE_COMBATE    = "combate"
FASE_FIM        = "fim"

def estado_inicial():
    return {
        "tabuleiros": [logic.criar_tabuleiro(), logic.criar_tabuleiro()],
        "fase": FASE_POSICIONAR,
        "jogador_atual": 0,
        "navios_colocados": [0, 0],
        "mensagem": "Jogador 1: Posicione seus navios",
        "mensagem_aviso": "",
        "aviso_timer": 0,
        "hover_celula": None,
        "vencedor": None,
        "aguardando_transicao": False,
    }

estado = estado_inicial()


def celula_para_pixel(linha, coluna):
    x = OFFSET_X + coluna * (TAMANHO_CELULA + MARGEM)
    y = OFFSET_Y + linha  * (TAMANHO_CELULA + MARGEM)
    return x, y


def pixel_para_celula(mx, my):
    for linha in range(logic.TAMANHO):
        for coluna in range(logic.TAMANHO):
            x, y = celula_para_pixel(linha, coluna)
            if x <= mx < x + TAMANHO_CELULA and y <= my < y + TAMANHO_CELULA:
                return linha, coluna
    return None, None


def desenhar_tabuleiro(tabuleiro, esconder_navios=False):
    hover = estado["hover_celula"]
    for linha in range(logic.TAMANHO):
        for coluna in range(logic.TAMANHO):
            x, y = celula_para_pixel(linha, coluna)
            valor = tabuleiro[linha][coluna]

            if valor == logic.ACERTO:
                cor = COR_ACERTO
            elif valor == logic.ERRO:
                cor = COR_ERRO
            elif valor == logic.NAVIO and not esconder_navios:
                cor = COR_NAVIO
            else:
                if hover == (linha, coluna):
                    cor = COR_AGUA_HOVER
                else:
                    cor = COR_AGUA

            pygame.draw.rect(tela, cor, (x, y, TAMANHO_CELULA, TAMANHO_CELULA), border_radius=4)
            pygame.draw.rect(tela, COR_GRADE, (x, y, TAMANHO_CELULA, TAMANHO_CELULA), 1, border_radius=4)

            if hover == (linha, coluna) and esconder_navios and valor not in (logic.ACERTO, logic.ERRO):
                pygame.draw.rect(tela, (255, 255, 255, 80), (x, y, TAMANHO_CELULA, TAMANHO_CELULA), border_radius=4)


def desenhar_preview_navio(linha, coluna):
    valido = coluna + logic.TAMANHO_NAVIO <= logic.TAMANHO
    if valido:
        for c in range(coluna, coluna + logic.TAMANHO_NAVIO):
            if estado["tabuleiros"][estado["jogador_atual"]][linha][c] != logic.VAZIO:
                valido = False
                break

    cor_preview = (100, 220, 100, 160) if valido else (220, 80, 80, 160)
    for dc in range(logic.TAMANHO_NAVIO):
        c = coluna + dc
        if 0 <= c < logic.TAMANHO:
            x, y = celula_para_pixel(linha, c)
            s = pygame.Surface((TAMANHO_CELULA, TAMANHO_CELULA), pygame.SRCALPHA)
            s.fill(cor_preview)
            tela.blit(s, (x, y))


def desenhar_texto_centralizado(texto, fonte, cor, y):
    surf = fonte.render(texto, True, cor)
    rect = surf.get_rect(center=(LARGURA // 2, y))
    tela.blit(surf, rect)


def desenhar_labels_grade():
    letras = "ABCDEFGHIJ"
    for i in range(logic.TAMANHO):
        x, y = celula_para_pixel(0, i)
        surf = FONTE_PEQUENA.render(letras[i], True, (150, 180, 230))
        tela.blit(surf, (x + TAMANHO_CELULA // 2 - surf.get_width() // 2, y - 18))

        x2, y2 = celula_para_pixel(i, 0)
        surf2 = FONTE_PEQUENA.render(str(i + 1), True, (150, 180, 230))
        tela.blit(surf2, (x2 - 20, y2 + TAMANHO_CELULA // 2 - surf2.get_height() // 2))


def desenhar_barra_navios():
    jog = estado["jogador_atual"]
    colocados = estado["navios_colocados"][jog]
    total = logic.TOTAL_NAVIOS
    texto = f"Navios colocados: {colocados} / {total}"
    surf = FONTE_MEDIA.render(texto, True, COR_AVISO)
    tela.blit(surf, (OFFSET_X, OFFSET_Y - 45))


def desenhar_tela_posicionar():
    tela.fill(COR_FUNDO)
    jog = estado["jogador_atual"] + 1
    desenhar_texto_centralizado(f"BATALHA NAVAL", FONTE_GRANDE, COR_VITORIA, 30)
    desenhar_texto_centralizado(estado["mensagem"], FONTE_MEDIA, COR_TEXTO, 70)

    tabuleiro = estado["tabuleiros"][estado["jogador_atual"]]
    desenhar_tabuleiro(tabuleiro, esconder_navios=False)
    desenhar_labels_grade()
    desenhar_barra_navios()

    hover = estado["hover_celula"]
    if hover:
        desenhar_preview_navio(hover[0], hover[1])

    if estado["aviso_timer"] > 0:
        desenhar_texto_centralizado(estado["mensagem_aviso"], FONTE_MEDIA, COR_AVISO, ALTURA - 50)

    surf_hint = FONTE_PEQUENA.render("Clique para posicionar • R = Reiniciar", True, (100, 130, 180))
    tela.blit(surf_hint, (OFFSET_X, ALTURA - 25))


def desenhar_tela_transicao():
    tela.fill(COR_FUNDO)
    jog = estado["jogador_atual"] + 1
    desenhar_texto_centralizado("PASSE O DISPOSITIVO", FONTE_GRANDE, COR_AVISO, ALTURA // 2 - 60)
    desenhar_texto_centralizado(f"Vez do Jogador {jog}", FONTE_MEDIA, COR_TEXTO, ALTURA // 2)
    desenhar_texto_centralizado("Pressione ESPAÇO para continuar", FONTE_PEQUENA, (150, 180, 220), ALTURA // 2 + 50)


def desenhar_tela_combate():
    tela.fill(COR_FUNDO)
    jog = estado["jogador_atual"]
    adversario = 1 - jog

    desenhar_texto_centralizado("BATALHA NAVAL", FONTE_GRANDE, COR_VITORIA, 30)
    desenhar_texto_centralizado(f"Vez do Jogador {jog + 1} — Ataque!", FONTE_MEDIA, COR_TEXTO, 70)

    desenhar_tabuleiro(estado["tabuleiros"][adversario], esconder_navios=True)
    desenhar_labels_grade()

    if estado["aviso_timer"] > 0:
        desenhar_texto_centralizado(estado["mensagem_aviso"], FONTE_MEDIA, COR_AVISO, ALTURA - 50)

    surf_hint = FONTE_PEQUENA.render("Clique no tabuleiro para atacar • R = Reiniciar", True, (100, 130, 180))
    tela.blit(surf_hint, (OFFSET_X, ALTURA - 25))


def desenhar_tela_fim():
    tela.fill(COR_FUNDO)
    vencedor = estado["vencedor"]
    desenhar_texto_centralizado("FIM DE JOGO!", FONTE_GRANDE, COR_AVISO, ALTURA // 2 - 80)
    desenhar_texto_centralizado(f"Jogador {vencedor} venceu!", FONTE_GRANDE, COR_VITORIA, ALTURA // 2 - 20)
    desenhar_texto_centralizado("Pressione R para jogar novamente", FONTE_MEDIA, COR_TEXTO, ALTURA // 2 + 60)


def definir_aviso(texto):
    estado["mensagem_aviso"] = texto
    estado["aviso_timer"] = 120


def handle_click_posicionar(linha, coluna):
    jog = estado["jogador_atual"]
    tabuleiro = estado["tabuleiros"][jog]

    sucesso = logic.posicionar_navio(tabuleiro, linha, coluna)
    if not sucesso:
        definir_aviso("Posição inválida!")
        return

    estado["navios_colocados"][jog] += 1

    if logic.navios_posicionados(tabuleiro):
        if jog == 0:
            estado["jogador_atual"] = 1
            estado["mensagem"] = "Jogador 2: Posicione seus navios"
            estado["fase"] = FASE_TRANSICAO
        else:
            estado["jogador_atual"] = 0
            estado["fase"] = FASE_TRANSICAO
            estado["mensagem_aviso"] = ""
            estado["aviso_timer"] = 0
            estado["fase"] = FASE_COMBATE
            estado["mensagem"] = "Vez do Jogador 1"


def handle_click_combate(linha, coluna):
    jog = estado["jogador_atual"]
    adversario = 1 - jog
    tabuleiro = estado["tabuleiros"][adversario]

    resultado = logic.atacar(tabuleiro, linha, coluna)

    if resultado == "ja_atacado":
        definir_aviso("Posição já atacada!")
        return

    if resultado == "acerto":
        definir_aviso("ACERTO!")
        if logic.todos_navios_destruidos(tabuleiro):
            estado["fase"] = FASE_FIM
            estado["vencedor"] = jog + 1
    else:
        definir_aviso("Água! Vez do adversário.")
        estado["jogador_atual"] = adversario


def processar_eventos():
    global estado
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_r:
                estado = estado_inicial()

            if evento.key == pygame.K_SPACE and estado["fase"] == FASE_TRANSICAO:
                if estado["jogador_atual"] == 1 and estado["navios_colocados"][0] > 0 and not logic.navios_posicionados(estado["tabuleiros"][1]):
                    estado["fase"] = FASE_POSICIONAR
                elif estado["jogador_atual"] == 0:
                    estado["fase"] = FASE_COMBATE
                    estado["mensagem"] = "Vez do Jogador 1"
                else:
                    estado["fase"] = FASE_POSICIONAR

        if evento.type == pygame.MOUSEMOTION:
            mx, my = evento.pos
            linha, coluna = pixel_para_celula(mx, my)
            if linha is not None:
                estado["hover_celula"] = (linha, coluna)
            else:
                estado["hover_celula"] = None

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            mx, my = evento.pos
            linha, coluna = pixel_para_celula(mx, my)
            if linha is None:
                continue

            if estado["fase"] == FASE_POSICIONAR:
                handle_click_posicionar(linha, coluna)

            elif estado["fase"] == FASE_COMBATE:
                handle_click_combate(linha, coluna)


def atualizar_timers():
    if estado["aviso_timer"] > 0:
        estado["aviso_timer"] -= 1


def desenhar():
    if estado["fase"] == FASE_POSICIONAR:
        desenhar_tela_posicionar()
    elif estado["fase"] == FASE_TRANSICAO:
        desenhar_tela_transicao()
    elif estado["fase"] == FASE_COMBATE:
        desenhar_tela_combate()
    elif estado["fase"] == FASE_FIM:
        desenhar_tela_fim()

    pygame.display.flip()


while True:
    processar_eventos()
    atualizar_timers()
    desenhar()
    relogio.tick(60)