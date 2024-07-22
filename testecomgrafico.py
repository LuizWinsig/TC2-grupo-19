from typing import List, Tuple

import numpy as np
import pygame
import random
from pygame.locals import *
import itertools
import matplotlib.pyplot as plt
import matplotlib.backends.backend_agg as agg

class Armazem:
    def __init__(self, localizacao: Tuple[int, int], nome_cidade: str, estoque_minimo: int):
        self.localizacao = localizacao
        self.nome_cidade = nome_cidade
        self.estoque_minimo = estoque_minimo

class Individuo:
    def __init__(self, veiculos: int, capacidade: int, rota: List[int]):
        self.veiculos = veiculos
        self.capacidade = capacidade
        self.rota = rota

    def __repr__(self):
        return f"Veículos: {self.veiculos}, Cap. Un.: {self.capacidade}, Cap. Total.: {self.veiculos * self.capacidade}"
    
    def calcular_fitness(self, capacidade_armazem_cidades: List[int], dist_matrix: List[List[float]]) -> float:
        capacidade_veiculo = self.capacidade
        rota = self.rota
        quantidade_veiculos = self.veiculos
        
        itens_por_armazem = [0] * len(capacidade_armazem_cidades) # Inicializa a quantidade de itens em cada armazém

        velocidade = 120 - capacidade_veiculo # A velocidade do veículo diminui conforme a capacidade aumenta

        tempo_total = 0

        while True:

            rota_a_percorrer = []

            for i in range(len(rota)):
                armazem = rota[i]

                if itens_por_armazem[armazem] < capacidade_armazem_cidades[armazem]:
                    rota_a_percorrer.append(armazem)

            if not rota_a_percorrer:
                break

            for i in range(len(rota_a_percorrer)):
                armazem = rota_a_percorrer[i]

                itens_por_armazem[armazem] += capacidade_veiculo * quantidade_veiculos

                if i == len(rota_a_percorrer) - 1:
                    distancia = 0
                else:
                    distancia = dist_matrix[rota_a_percorrer[i]][rota_a_percorrer[i+1]]

                tempo = round(distancia / velocidade, 2)

                tempo_total += tempo * quantidade_veiculos

        return round(tempo_total, 2)

def calcular_matriz_distancias(
    local_cidades: List[Tuple[int, int]]
) -> List[List[float]]:
    dist_matrix = np.zeros((len(local_cidades), len(local_cidades)))

    for i in range(len(local_cidades)):
        for j in range(len(local_cidades)):
            x1, y1 = local_cidades[i]
            x2, y2 = local_cidades[j]
            distance = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            dist_matrix[i][j] = distance

    return dist_matrix

def gerar_populacao(
    local_cidades: List[Tuple[int, int]],
    maximo_veiculos: int,
    capacidade_maxima: int,
    tamanho_populacao: int,
) -> List[Individuo]:
    populacao = []
    for _ in range(tamanho_populacao):
        veiculo = random.randint(1, maximo_veiculos)
        capacidade = random.randint(1, capacidade_maxima)

        rota = random.sample(range(len(local_cidades)), len(local_cidades))
        individuo = Individuo(veiculo, capacidade, rota)

        populacao.append(individuo)
    return populacao

def order_crossover(pai1: Individuo, pai2: Individuo) -> Individuo:
    tamanho = len(pai1.rota)
    start_index = random.randint(0, tamanho - 1)
    end_index = random.randint(start_index + 1, tamanho)
    filho = Individuo(pai1.veiculos, pai1.capacidade, [])
    filho.rota.extend(pai1.rota[start_index:end_index])
    remaining_positions = [
        i for i in range(tamanho) if i < start_index or i >= end_index
    ]
    remaining_genes = [gene for gene in pai2.rota if gene not in filho.rota]
    for position, gene in zip(remaining_positions, remaining_genes):
        filho.rota.insert(position, gene)
    return filho

def mutate(solution: Individuo, mutation_probability: float) -> Individuo:
    if random.random() < mutation_probability:
        index1 = random.randint(0, len(solution.rota) - 1)
        index2 = random.randint(0, len(solution.rota) - 1)
        solution.rota[index1], solution.rota[index2] = (
            solution.rota[index2],
            solution.rota[index1],
        )
    return solution

def init_screen(width: int, height: int, caption: str) -> pygame.Surface:
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(caption)
    return screen

def desenhar_rotas(screen, melhor_rota, armazens):
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    screen.fill(WHITE)
    font = pygame.font.Font(None, 20)
    for armazem in armazens:
        x, y = armazem.localizacao
        pygame.draw.circle(screen, BLUE, (x, y), 5)
        text = font.render(armazem.nome_cidade, True, WHITE)
        text_rect = text.get_rect(center=(x - 15, y - 15))
        screen.blit(text, text_rect)
    for i in range(len(melhor_rota)):
        cidade_atual = melhor_rota[i]
        proxima_cidade = melhor_rota[(i + 1) % len(melhor_rota)]
        pygame.draw.line(
            screen,
            RED,
            armazens[cidade_atual].localizacao,
            armazens[proxima_cidade].localizacao,
            2,
        )
        text = font.render(f"({i + 1})", True, WHITE)
        x, y = armazens[cidade_atual].localizacao
        text_rect = text.get_rect(center=(x - 20, y - 30))
        screen.blit(text, text_rect)
    pygame.display.flip()

def desenhar_info(screen, geracao, melhor_tempo, melhor_individuo):
    font = pygame.font.Font(None, 20)
    GREEN = (0, 255, 0)
    text = font.render(f"Geração: {geracao}", True, GREEN)   
    screen.blit(text, (10, 500))
    if melhor_individuo:
        text = font.render(f"Melhor indivíduo: {melhor_individuo}", True, GREEN)
        screen.blit(text, (10, 520))
        text = font.render(f"Melhor tempo: {melhor_tempo}", True, GREEN)
        screen.blit(text, (10, 540))
        pygame.display.flip()

def plotar_graficos(geracoes, custos):
    plt.figure(figsize=(12, 6))

    plt.subplot(1, 2, 1)
    plt.plot(geracoes, custos, label='Custo Total')
    plt.xlabel('Geração')
    plt.ylabel('Custo')
    plt.title('Evolução do Custo ao Longo das Gerações')
    plt.legend()
    plt.grid(True)


    plt.tight_layout()


def renderizar_grafico(screen, fig, posicao, width, height):
    canvas = agg.FigureCanvasAgg(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.tostring_rgb()
    size = canvas.get_width_height()

    surf = pygame.image.fromstring(raw_data, size, "RGB")
    surf = pygame.transform.scale(surf, (width, height))
    screen.blit(surf, posicao)
    pygame.display.flip()


def metodo_selecao_aleatorio(populacao_fitness):
    pai1_fitness, pai2_fitness = random.choices(populacao_fitness[:10], k=2)
    pai1 = pai1_fitness[0]
    pai2 = pai2_fitness[0]
    return pai1, pai2

def metodo_selecao_torneio(populacao_fitness):
    def torneio(populacao_fitness):
        tamanho_torneio = 3
        participantes = random.sample(populacao_fitness, tamanho_torneio)
        participantes.sort(key=lambda x: x[1])
        return participantes[0]
    
    pai1_fitness = torneio(populacao_fitness)
    pai2_fitness = torneio(populacao_fitness)
    return pai1_fitness[0], pai2_fitness[0]

def algoritmo_genetico(
    armazens: List[Armazem],
    tamanho_populacao: int,
    geracoes: int,
    capacidade_maxima: int,
    capacidade_armazem_cidades: List[int],
    dist_matrix: List[List[float]],
    metodo_de_selecao,
) -> Individuo:
    maximo_veiculos = 4
    populacao = gerar_populacao(
        [armazem.localizacao for armazem in armazens],
        maximo_veiculos,
        capacidade_maxima,
        tamanho_populacao,
    )
    melhor_individuo = None
    melhor_tempo = float("inf")
    melhor_individuos_por_geracao = []
    tempos_por_geracao = []
    lista_geracoes = []
    for geracao in range(geracoes):
        lista_geracoes.append(geracao)
        populacao_fitness = [
            (individuo, individuo.calcular_fitness(capacidade_armazem_cidades, dist_matrix))
            for individuo in populacao
        ]
        populacao_fitness.sort(key=lambda x: x[1])
        if populacao_fitness[0][1] < melhor_tempo:
            melhor_tempo = populacao_fitness[0][1]
            melhor_individuo = populacao_fitness[0][0]
        nova_populacao = populacao_fitness[:2]
        while len(nova_populacao) < tamanho_populacao:
            pai1, pai2 = metodo_de_selecao(populacao_fitness)
            filho = order_crossover(pai1, pai2)
            filho_mutado = mutate(filho, 0.1)
            nova_populacao.append((filho_mutado, filho_mutado.calcular_fitness(capacidade_armazem_cidades, dist_matrix)))
        populacao = [individuo for individuo, _ in nova_populacao]
        melhor_individuos_por_geracao.append(melhor_individuo)
        tempos_por_geracao.append(melhor_tempo)
        
        screen = init_screen(800, 800, "Algoritmo Genético - Otimização de Rotas")
        WIDTH, HEIGHT = 800, 800
        PERCENTUAL_MARGEM_TELA = 0.07  # 7% de margem
        margin_x = int(WIDTH * PERCENTUAL_MARGEM_TELA)
        margin_y = int(HEIGHT * PERCENTUAL_MARGEM_TELA)
        
        desenhar_rotas(screen, melhor_individuo.rota, armazens)
        plotar_graficos(range(1, len(lista_geracoes) + 1), tempos_por_geracao)
        renderizar_grafico(screen, plt.gcf(), (margin_x, HEIGHT // 2 + margin_y), WIDTH - 2 * margin_x, HEIGHT // 2 - 2 * margin_y)

        desenhar_info(screen, geracao, melhor_tempo, melhor_individuo)
    return melhor_individuo

def main():
    armazens=[]
    WIDTH, HEIGHT = 800, 800
    TAMANHO_POPULACAO = 500
    TOTAL_GERACOES = 100
    CAPACIDADE_MAXIMA = 50
    MAXIMO_VEICULOS = 10
    PROBABILIDADE_MUTACAO = 0.7

    PERCENTUAL_MARGEM_TELA = 0.07  # 7% de margem
    margin_x = int(WIDTH * PERCENTUAL_MARGEM_TELA)
    margin_y = int(HEIGHT * PERCENTUAL_MARGEM_TELA)
    
    NOMES_CIDADES = ["Tokyo", "New York", "Paris", "Berlim", "Roma", "Pequim", "Madrid", "Washington", "Brasilia", "Montevideo"]
    LOCAL_CIDADES = [(random.randint(margin_x, WIDTH - margin_x), random.randint(margin_y, HEIGHT - margin_y - 100)) for _ in range(len(NOMES_CIDADES))]
    ESTOQUE_MINIMO_CIDADES = [7000, 4200, 3500, 2500, 5000, 6000, 3000, 2500, 1800, 4200]
        
    
    #screen = init_screen(800, 600, "Algoritmo Genético - Otimização de Rotas")
    
    for local_cidade, nome_cidade, estoque in zip(LOCAL_CIDADES, NOMES_CIDADES, ESTOQUE_MINIMO_CIDADES):
        armazem = Armazem(local_cidade, nome_cidade, estoque)
        armazens.append(armazem)
        
    
    capacidade_maxima = 15
    capacidade_armazem_cidades = [armazem.estoque_minimo for armazem in armazens]
    local_cidades = [armazem.localizacao for armazem in armazens]
    dist_matrix = calcular_matriz_distancias(local_cidades)
    melhor_individuo = algoritmo_genetico(
        armazens, 20, 100, capacidade_maxima, capacidade_armazem_cidades, dist_matrix, metodo_selecao_aleatorio
    )
    print("Melhor indivíduo encontrado:", melhor_individuo)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()
