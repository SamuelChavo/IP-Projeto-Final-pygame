import pygame
import sys
import math
import random
import logic

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)

LARGURA = 700
ALTURA  = 750
TAMANHO_CELULA = 52
MARGEM   = 2
OFFSET_X = 35
OFFSET_Y = 140

tela    = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Batalha Naval")
relogio = pygame.time.Clock()

AZUL_FUNDO  = (10,  20,  45)
AZUL_ESCURO = (15,  30,  65)
AZUL_MAR    = (25,  75, 155)
AZUL_HOVER  = (45, 110, 210)
AZUL_GRADE  = (15,  45, 100)
VERDE_NAVIO = (60, 170,  70)
VERMELHO    = (210,  50,  50)
CINZA_ERRO  = (160, 170, 200)
BRANCO      = (240, 245, 255)
AMARELO     = (255, 205,  55)
CIANO       = ( 80, 220, 200)
LARANJA     = (255, 140,  40)
PRETO       = (  5,   8,  20)

try:
    FONTE_TITULO  = pygame.font.SysFont("verdana", 46, bold=True)
    FONTE_GRANDE  = pygame.font.SysFont("verdana", 30)
    FONTE_MEDIA   = pygame.font.SysFont("segoeui", 21)
    FONTE_PEQUENA = pygame.font.SysFont("segoeui", 15)
    FONTE_MINI    = pygame.font.SysFont("segoeui", 13)
except:
    FONTE_TITULO  = pygame.font.SysFont(None, 52)
    FONTE_GRANDE  = pygame.font.SysFont(None, 34)
    FONTE_MEDIA   = pygame.font.SysFont(None, 21)
    FONTE_PEQUENA = pygame.font.SysFont(None, 15)
    FONTE_MINI    = pygame.font.SysFont(None, 13)


def gerar_som_explosao():
    taxa = 44100
    dur  = 0.45
    n    = int(taxa * dur)
    buf  = bytearray(n * 2)
    for i in range(n):
        t     = i / taxa
        decay = math.exp(-t * 9)
        ruido = random.uniform(-1, 1)
        boom  = math.sin(2 * math.pi * 60 * t) * math.exp(-t * 5)
        val   = int((ruido * 0.6 + boom * 0.4) * decay * 28000)
        val   = max(-32768, min(32767, val))
        buf[i*2]   = val & 0xFF
        buf[i*2+1] = (val >> 8) & 0xFF
    return pygame.mixer.Sound(buffer=bytes(buf))


def gerar_som_agua():
    taxa = 44100
    dur  = 0.3
    n    = int(taxa * dur)
    buf  = bytearray(n * 2)
    for i in range(n):
        t      = i / taxa
        decay  = math.exp(-t * 12)
        ruido  = random.uniform(-1, 1)
        splash = math.sin(2 * math.pi * 400 * t) * math.exp(-t * 20)
        val    = int((ruido * 0.3 + splash * 0.7) * decay * 18000)
        val    = max(-32768, min(32767, val))
        buf[i*2]   = val & 0xFF
        buf[i*2+1] = (val >> 8) & 0xFF
    return pygame.mixer.Sound(buffer=bytes(buf))


def gerar_som_vitoria():
    taxa  = 44100
    dur   = 1.2
    n     = int(taxa * dur)
    buf   = bytearray(n * 2)
    notas = [523, 659, 784, 1047]
    for i in range(n):
        t    = i / taxa
        idx  = min(int(t / 0.3), 3)
        freq = notas[idx]
        decay = math.exp(-(t - idx * 0.3) * 4)
        val   = int(math.sin(2 * math.pi * freq * t) * decay * 22000)
        val   = max(-32768, min(32767, val))
        buf[i*2]   = val & 0xFF
        buf[i*2+1] = (val >> 8) & 0xFF
    return pygame.mixer.Sound(buffer=bytes(buf))


def gerar_som_clique():
    taxa = 44100
    dur  = 0.06
    n    = int(taxa * dur)
    buf  = bytearray(n * 2)
    for i in range(n):
        t   = i / taxa
        val = int(math.sin(2 * math.pi * 900 * t) * math.exp(-t * 40) * 14000)
        val = max(-32768, min(32767, val))
        buf[i*2]   = val & 0xFF
        buf[i*2+1] = (val >> 8) & 0xFF
    return pygame.mixer.Sound(buffer=bytes(buf))


SOM_EXPLOSAO = gerar_som_explosao()
SOM_AGUA     = gerar_som_agua()
SOM_VITORIA  = gerar_som_vitoria()
SOM_CLIQUE   = gerar_som_clique()

FASE_MENU       = "menu"
FASE_REGRAS     = "regras"
FASE_POSICIONAR = "posicionar"
FASE_TRANSICAO  = "transicao"
FASE_COMBATE    = "combate"
FASE_FIM        = "fim"

particulas = []
estrelas   = [(random.randint(0, LARGURA), random.randint(0, ALTURA),
               random.uniform(0.3, 1.2)) for _ in range(80)]


def estado_inicial():
    return {
        "tabuleiros":        [logic.criar_tabuleiro(), logic.criar_tabuleiro()],
        "fase":              FASE_MENU,
        "jogador_atual":     0,
        "navios_colocados":  [0, 0],
        "mensagem_aviso":    "",
        "aviso_timer":       0,
        "hover_celula":      None,
        "vencedor":          None,
        "tick":              0,
        "vitoria_timer":     0,
        "proximo_combate":   False,
    }


estado = estado_inicial()


def adicionar_particulas(x, y, cor, qtd=18, explosao=False):
    for _ in range(qtd):
        ang = random.uniform(0, 2 * math.pi)
        vel = random.uniform(2, 9) if explosao else random.uniform(1, 4)
        particulas.append({
            "x": x, "y": y,
            "vx": math.cos(ang) * vel,
            "vy": math.sin(ang) * vel - (3 if explosao else 1),
            "vida": random.randint(25, 55),
            "max_vida": 50,
            "cor": cor,
            "tam": random.randint(3, 8) if explosao else random.randint(2, 5),
        })


def atualizar_particulas():
    for p in particulas:
        p["x"]  += p["vx"]
        p["y"]  += p["vy"]
        p["vy"] += 0.18
        p["vida"] -= 1
    particulas[:] = [p for p in particulas if p["vida"] > 0]


def desenhar_particulas():
    for p in particulas:
        a = p["vida"] / p["max_vida"]

        cor = (
            max(0, min(255, int(p["cor"][0] * a))),
            max(0, min(255, int(p["cor"][1] * a))),
            max(0, min(255, int(p["cor"][2] * a)))
        )

        tam = max(1, int(p["tam"] * a))
        pygame.draw.circle(tela, cor, (int(p["x"]), int(p["y"])), tam)


def desenhar_estrelas(tick):
    for (sx, sy, brilho) in estrelas:
        pulso = abs(math.sin(tick * 0.02 + sx * 0.1)) * brilho
        val   = min(255, int(60 + pulso * 120))
        pygame.draw.circle(tela, (val, val, min(255, val + 30)), (sx, sy), 1)


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


def texto_centralizado(texto, fonte, cor, y, alpha=255):
    surf = fonte.render(texto, True, cor)
    if alpha < 255:
        surf.set_alpha(alpha)
    tela.blit(surf, surf.get_rect(center=(LARGURA // 2, y)))


def desenhar_botao(texto, rect, hover=False, fonte=None):
    if fonte is None:
        fonte = FONTE_MEDIA
    fundo = (30, 75, 160) if hover else (20, 50, 110)
    borda = CIANO         if hover else (80, 120, 200)
    pygame.draw.rect(tela, fundo, rect, border_radius=10)
    pygame.draw.rect(tela, borda, rect, 2, border_radius=10)
    surf = fonte.render(texto, True, BRANCO)
    tela.blit(surf, surf.get_rect(center=rect.center))


def desenhar_tabuleiro(tabuleiro, esconder_navios=False):
    hover = estado["hover_celula"]
    tick  = estado["tick"]
    for linha in range(logic.TAMANHO):
        for coluna in range(logic.TAMANHO):
            x, y  = celula_para_pixel(linha, coluna)
            valor = tabuleiro[linha][coluna]

            if valor == logic.ACERTO:
                cor = VERMELHO
            elif valor == logic.ERRO:
                cor = CINZA_ERRO
            elif valor == logic.NAVIO and not esconder_navios:
                cor = VERDE_NAVIO
            else:
                if hover == (linha, coluna):
                    cor = AZUL_HOVER
                else:
                    ond = int(math.sin(tick * 0.04 + coluna * 0.3 + linha * 0.2) * 8)
                    cor = (AZUL_MAR[0],max(0, min(255, AZUL_MAR[1] + ond)),max(0, min(255, AZUL_MAR[2] + ond * 2)))

            pygame.draw.rect(tela, cor, (x, y, TAMANHO_CELULA, TAMANHO_CELULA), border_radius=5)
            pygame.draw.rect(tela, AZUL_GRADE, (x, y, TAMANHO_CELULA, TAMANHO_CELULA), 1, border_radius=5)

            if valor == logic.ACERTO:
                cx = x + TAMANHO_CELULA // 2
                cy = y + TAMANHO_CELULA // 2
                pygame.draw.line(tela, (255, 200, 200), (cx-10, cy-10), (cx+10, cy+10), 3)
                pygame.draw.line(tela, (255, 200, 200), (cx+10, cy-10), (cx-10, cy+10), 3)
            elif valor == logic.ERRO:
                cx = x + TAMANHO_CELULA // 2
                cy = y + TAMANHO_CELULA // 2
                pygame.draw.circle(tela, (100, 120, 180), (cx, cy), 6)


def desenhar_preview_navio(linha, coluna):
    valido = coluna + logic.TAMANHO_NAVIO <= logic.TAMANHO
    if valido:
        for c in range(coluna, coluna + logic.TAMANHO_NAVIO):
            if estado["tabuleiros"][estado["jogador_atual"]][linha][c] != logic.VAZIO:
                valido = False
                break
    cor = (80, 220, 80, 170) if valido else (220, 60, 60, 170)
    for dc in range(logic.TAMANHO_NAVIO):
        c = coluna + dc
        if 0 <= c < logic.TAMANHO:
            x, y = celula_para_pixel(linha, c)
            s = pygame.Surface((TAMANHO_CELULA, TAMANHO_CELULA), pygame.SRCALPHA)
            s.fill(cor)
            pygame.draw.rect(s, (255, 255, 255, 60), (0, 0, TAMANHO_CELULA, TAMANHO_CELULA), 2, border_radius=5)
            tela.blit(s, (x, y))


def desenhar_labels_grade():
    letras = "ABCDEFGHIJ"
    for i in range(logic.TAMANHO):
        x, y = celula_para_pixel(0, i)
        surf = FONTE_MINI.render(letras[i], True, CIANO)
        tela.blit(surf, (x + TAMANHO_CELULA // 2 - surf.get_width() // 2, y - 18))
        x2, y2 = celula_para_pixel(i, 0)
        surf2 = FONTE_MINI.render(str(i + 1), True, CIANO)
        tela.blit(surf2, (x2 - 18, y2 + TAMANHO_CELULA // 2 - surf2.get_height() // 2))


def desenhar_pip_navios():
    jog      = estado["jogador_atual"]
    colocados = estado["navios_colocados"][jog]
    total    = logic.TOTAL_NAVIOS
    sx, sy   = OFFSET_X, OFFSET_Y - 55
    surf = FONTE_PEQUENA.render("Navios: ", True, (150, 180, 220))
    tela.blit(surf, (sx, sy + 2))
    ox = sx + surf.get_width() + 4
    for i in range(total):
        cor = VERDE_NAVIO if i < colocados else (40, 60, 100)
        pygame.draw.rect(tela, cor, (ox + i * 30, sy, 25, 10), border_radius=3)


def botoes_menu():
    return [
        (pygame.Rect(LARGURA//2 - 150, 230,       300, 52), FASE_POSICIONAR, "JOGAR (2 JOGADORES)"),
        (pygame.Rect(LARGURA//2 - 150, 230 + 80,  300, 52), FASE_REGRAS,     "REGRAS"),
        (pygame.Rect(LARGURA//2 - 150, 230 + 160, 300, 52), "sair",          "SAIR"),
    ]


def desenhar_tela_menu():
    tela.fill(AZUL_FUNDO)
    tick = estado["tick"]
    pulso = abs(math.sin(tick * 0.04)) * 15
    desenhar_estrelas(tick)

    for i in range(0, LARGURA, 54):
        ond1 = math.sin(tick * 0.025 + i * 0.05) * 18
        ond2 = math.sin(tick * 0.025 + (i + 54) * 0.05) * 18
        pygame.draw.line(tela, (18, 38, 85),
                         (i,      ALTURA - 100 + int(ond1)),
                         (i + 54, ALTURA - 100 + int(ond2)), 2)

    cor_tit = (
        min(255, int(80 + pulso)),
        min(255, int(180 + pulso // 2)),
        min(255, int(200 + pulso))
    )
    texto_centralizado("BATALHA NAVAL", FONTE_TITULO, cor_tit, 95)

    sub = FONTE_PEQUENA.render("— JOGO ESTRATÉGICO —", True, (80, 130, 180))
    tela.blit(sub, sub.get_rect(center=(LARGURA // 2, 145)))

    mx, my = pygame.mouse.get_pos()
    for rect, _, label in botoes_menu():
        hover = rect.collidepoint(mx, my)
        desenhar_botao(label, rect, hover)

    dica = FONTE_MINI.render("v1.0  •  Feito com pygame", True, (40, 65, 110))
    tela.blit(dica, (LARGURA - dica.get_width() - 10, ALTURA - 20))


def desenhar_tela_regras():
    tela.fill(AZUL_FUNDO)
    desenhar_estrelas(estado["tick"])
    texto_centralizado("REGRAS DO JOGO", FONTE_GRANDE, CIANO, 45)

    linhas = [
        "Cada jogador posiciona 7 navios no tabuleiro 10x10.",
        "Cada navio ocupa 3 casas na horizontal.",
        "Clique na célula mais à esquerda para posicionar.",
        "Na fase de combate, clique no tabuleiro adversário.",
        "Acertar um navio destrói ele por completo!",
        "Se acertar, você joga de novo. Se errar, passa a vez.",
        "Vence quem destruir todos os navios do adversário.",
        "",
        "R = Reiniciar   |   ESPAÇO = Confirmar transição",
    ]
    for i, linha in enumerate(linhas):
        cor  = AMARELO if i == len(linhas) - 1 else BRANCO
        surf = FONTE_PEQUENA.render(linha, True, cor)
        tela.blit(surf, surf.get_rect(center=(LARGURA // 2, 110 + i * 38)))

    mx, my   = pygame.mouse.get_pos()
    rect_vol = pygame.Rect(LARGURA // 2 - 120, ALTURA - 90, 240, 50)
    desenhar_botao("VOLTAR AO MENU", rect_vol, rect_vol.collidepoint(mx, my))


def desenhar_tela_posicionar():
    tela.fill(AZUL_ESCURO)
    desenhar_estrelas(estado["tick"])
    jog = estado["jogador_atual"] + 1
    texto_centralizado(f"JOGADOR {jog}  —  POSICIONE SEUS NAVIOS", FONTE_GRANDE, CIANO, 35)
    texto_centralizado("Clique para posicionar • Navio ocupa 3 casas à direita", FONTE_PEQUENA, (130, 170, 220), 68)

    desenhar_tabuleiro(estado["tabuleiros"][estado["jogador_atual"]])
    desenhar_labels_grade()
    desenhar_pip_navios()

    hover = estado["hover_celula"]
    if hover:
        desenhar_preview_navio(hover[0], hover[1])

    if estado["aviso_timer"] > 0:
        alpha = min(255, estado["aviso_timer"] * 4)
        texto_centralizado(estado["mensagem_aviso"], FONTE_MEDIA, AMARELO, ALTURA - 45, alpha)

    surf = FONTE_MINI.render("R = Reiniciar", True, (60, 90, 140))
    tela.blit(surf, (LARGURA - surf.get_width() - 10, ALTURA - 18))


def desenhar_tela_transicao():
    tela.fill(AZUL_FUNDO)
    desenhar_estrelas(estado["tick"])
    tick  = estado["tick"]
    pulso = abs(math.sin(tick * 0.05)) * 30

    texto_centralizado("PASSE O DISPOSITIVO", FONTE_GRANDE, AMARELO, ALTURA // 2 - 70)
    texto_centralizado(f"Vez do Jogador {estado['jogador_atual'] + 1}", FONTE_MEDIA, BRANCO, ALTURA // 2)
    texto_centralizado("Não olhe para o tabuleiro do adversário!", FONTE_PEQUENA, (160, 190, 230), ALTURA // 2 + 45)

    cor_esp = (int(80 + pulso), int(180 + pulso), int(220 + pulso // 2))
    texto_centralizado("[ ESPAÇO ] para continuar", FONTE_MEDIA, cor_esp, ALTURA // 2 + 100)


def desenhar_tela_combate():
    tela.fill(AZUL_ESCURO)
    desenhar_estrelas(estado["tick"])
    jog = estado["jogador_atual"]
    texto_centralizado(f"JOGADOR {jog + 1}  —  ATAQUE!", FONTE_GRANDE, CIANO, 35)
    texto_centralizado("Clique em uma célula do tabuleiro inimigo", FONTE_PEQUENA, (130, 170, 220), 68)

    desenhar_tabuleiro(estado["tabuleiros"][1 - jog], esconder_navios=True)
    desenhar_labels_grade()

    if estado["aviso_timer"] > 0:
        alpha = min(255, estado["aviso_timer"] * 4)
        cor   = VERMELHO if "ACERTO" in estado["mensagem_aviso"] else AMARELO
        texto_centralizado(estado["mensagem_aviso"], FONTE_MEDIA, cor, ALTURA - 45, alpha)

    surf = FONTE_MINI.render("R = Reiniciar", True, (60, 90, 140))
    tela.blit(surf, (LARGURA - surf.get_width() - 10, ALTURA - 18))


def desenhar_tela_fim():
    tela.fill(PRETO)
    desenhar_estrelas(estado["tick"])
    tick = estado["tick"]
    vt   = estado["vitoria_timer"]
    venc = estado["vencedor"]

    if vt > 10:
        escala = abs(math.sin(tick * 0.04)) * 8
        cor = (
        min(255, int(80 + escala * 3)),
        min(255, int(200 + escala)),
        min(255, int(120 + escala * 2))
    )
        texto_centralizado("VITÓRIA!", FONTE_TITULO, cor, ALTURA // 2 - 90, min(255, (vt-10)*8))

    if vt > 30:
        texto_centralizado(f"Jogador {venc} dominou os mares!", FONTE_GRANDE, BRANCO, ALTURA // 2, min(255, (vt-30)*6))

    if vt > 55:
        texto_centralizado("Todos os navios inimigos foram afundados.", FONTE_PEQUENA, (150, 200, 230), ALTURA // 2 + 55, min(255, (vt-55)*5))

    if vt > 80:
        texto_centralizado("Pressione R para jogar novamente", FONTE_MEDIA, AMARELO, ALTURA // 2 + 120, min(255, (vt-80)*5))

    if tick % 18 == 0 and vt > 20:
        x = random.randint(100, LARGURA - 100)
        y = random.randint(100, ALTURA  - 200)
        adicionar_particulas(x, y, random.choice([AMARELO, LARANJA, CIANO, BRANCO]), qtd=14, explosao=True)


def definir_aviso(texto):
    estado["mensagem_aviso"] = texto
    estado["aviso_timer"]    = 130


def handle_click_posicionar(linha, coluna):
    jog = estado["jogador_atual"]
    tab = estado["tabuleiros"][jog]

    if not logic.posicionar_navio(tab, linha, coluna):
        definir_aviso("Posição inválida!")
        SOM_CLIQUE.play()
        return

    SOM_CLIQUE.play()
    cx, cy = celula_para_pixel(linha, coluna + 1)
    adicionar_particulas(cx + TAMANHO_CELULA // 2, cy + TAMANHO_CELULA // 2, VERDE_NAVIO, qtd=8)
    estado["navios_colocados"][jog] += 1

    if logic.navios_posicionados(tab):
        if jog == 0:
            estado["jogador_atual"]  = 1
            estado["proximo_combate"] = False
            estado["fase"]           = FASE_TRANSICAO
        else:
            estado["jogador_atual"]  = 0
            estado["proximo_combate"] = True
            estado["fase"]           = FASE_TRANSICAO


def handle_click_combate(linha, coluna):
    jog = estado["jogador_atual"]
    adv = 1 - jog
    tab = estado["tabuleiros"][adv]

    resultado = logic.atacar(tab, linha, coluna)
    cx, cy    = celula_para_pixel(linha, coluna)
    cx       += TAMANHO_CELULA // 2
    cy       += TAMANHO_CELULA // 2

    if resultado == "ja_atacado":
        definir_aviso("Posição já atacada!")
        SOM_CLIQUE.play()
        return

    if resultado == "acerto":
        SOM_EXPLOSAO.play()
        adicionar_particulas(cx, cy, VERMELHO, qtd=20, explosao=True)
        adicionar_particulas(cx, cy, LARANJA,  qtd=12, explosao=True)
        adicionar_particulas(cx, cy, AMARELO,  qtd=8,  explosao=True)
        definir_aviso("ACERTO! Ataque novamente.")
        if logic.todos_navios_destruidos(tab):
            estado["fase"]          = FASE_FIM
            estado["vencedor"]      = jog + 1
            estado["vitoria_timer"] = 0
            SOM_VITORIA.play()
    else:
        SOM_AGUA.play()
        adicionar_particulas(cx, cy, (100, 160, 255), qtd=10)
        definir_aviso("Água! Vez do adversário.")
        estado["jogador_atual"] = adv


def processar_eventos():
    global estado
    mx, my = pygame.mouse.get_pos()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_r:
                estado = estado_inicial()
                particulas.clear()

            if evento.key == pygame.K_SPACE and estado["fase"] == FASE_TRANSICAO:
                if estado["proximo_combate"]:
                    estado["fase"] = FASE_COMBATE
                else:
                    estado["fase"] = FASE_POSICIONAR

        if evento.type == pygame.MOUSEMOTION:
            linha, coluna = pixel_para_celula(mx, my)
            estado["hover_celula"] = (linha, coluna) if linha is not None else None

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            fase = estado["fase"]

            if fase == FASE_MENU:
                for rect, acao, _ in botoes_menu():
                    if rect.collidepoint(mx, my):
                        SOM_CLIQUE.play()
                        if acao == "sair":
                            pygame.quit()
                            sys.exit()
                        estado["fase"] = acao

            elif fase == FASE_REGRAS:
                rect_vol = pygame.Rect(LARGURA // 2 - 120, ALTURA - 90, 240, 50)
                if rect_vol.collidepoint(mx, my):
                    SOM_CLIQUE.play()
                    estado["fase"] = FASE_MENU

            elif fase == FASE_POSICIONAR:
                linha, coluna = pixel_para_celula(mx, my)
                if linha is not None:
                    handle_click_posicionar(linha, coluna)

            elif fase == FASE_COMBATE:
                linha, coluna = pixel_para_celula(mx, my)
                if linha is not None:
                    handle_click_combate(linha, coluna)


def atualizar():
    estado["tick"] += 1
    if estado["aviso_timer"] > 0:
        estado["aviso_timer"] -= 1
    if estado["fase"] == FASE_FIM:
        estado["vitoria_timer"] += 1
    atualizar_particulas()


def desenhar():
    fase = estado["fase"]
    if fase == FASE_MENU:
        desenhar_tela_menu()
    elif fase == FASE_REGRAS:
        desenhar_tela_regras()
    elif fase == FASE_POSICIONAR:
        desenhar_tela_posicionar()
    elif fase == FASE_TRANSICAO:
        desenhar_tela_transicao()
    elif fase == FASE_COMBATE:
        desenhar_tela_combate()
    elif fase == FASE_FIM:
        desenhar_tela_fim()

    desenhar_particulas()
    pygame.display.flip()


while True:
    processar_eventos()
    atualizar()
    desenhar()
    relogio.tick(60)
