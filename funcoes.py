import random
from typing import List, Tuple

import numpy as np
import pygame
from tipos import Individuo
import matplotlib.pyplot as plt
import matplotlib.backends.backend_agg as agg


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

# Função para inicializar a tela do Pygame
def init_screen(width: int, height: int, caption: str) -> pygame.Surface:
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(caption)
    return screen

def desenhar_rotas(screen, melhor_rota, armazens):
    
    # Cores
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)

    # Limpa a tela
    screen.fill(BLACK)

    font = pygame.font.Font(None, 20)
    
    # Desenha os pontos (dots) na tela
    for armazem in armazens:
        x, y = armazem.localizacao
        pygame.draw.circle(screen, BLUE, (x, y), 5)
        
        text = font.render(armazem.nome_cidade, True, WHITE)
        text_rect = text.get_rect(center=(x - 15, y - 15))
        screen.blit(text, text_rect)
    
    # Desenha as linhas da melhor rota
    for i in range(len(melhor_rota)):
        cidade_atual = melhor_rota[i]
        proxima_cidade = melhor_rota[(i + 1) % len(melhor_rota)]
        # print(i, (i+1), cidade_atual, proxima_cidade)
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

    pygame.display.flip()  # Atualiza a tela

def desenhar_info(screen, geracao, melhor_tempo, melhor_individuo, metodo_selecao_escolhido):
    font = pygame.font.Font(None, 20)
    GREEN = (0, 255, 0)

    text = font.render(f"Geração: {geracao}", True, GREEN)  
    screen.blit(text, (10, 700))

    if melhor_individuo:
        
        text = font.render(f"Melhor indivíduo: {melhor_individuo}", True, GREEN)
        screen.blit(text, (10, 720))
        text = font.render(f"Melhor tempo: {melhor_tempo}", True, GREEN)
        screen.blit(text, (10, 540))
        pygame.display.flip()

    
def metodo_selecao_aleatorio(populacao_fitness): #elitista aleatorio (aleatorio entre os 10 melhores)
    pai1_fitness, pai2_fitness = random.choices(populacao_fitness[:10], k=2)
    pai1 = pai1_fitness[0]
    pai2 = pai2_fitness[0]
    return pai1, pai2

def metodo_selecao_torneio(populacao_fitness):
    def torneio(populacao_fitness):
        tamanho_torneio = 3 # Tamanho do torneio igual a 3 competidores
        competidores = random.sample(populacao_fitness, tamanho_torneio)
        competidores.sort(key=lambda x: x[1])  # Ordena por fitness
        return competidores[0][0]  # Retorna o melhor competidor

    pai1 = torneio(populacao_fitness[:10])
    pai2 = torneio(populacao_fitness[:10])
    return pai1, pai2

def metodo_selecao_roleta(populacao_fitness):
    # Calcula a soma total dos fitness para calcular as probabilidades
    soma_fitness = sum(fitness for _, fitness in populacao_fitness)

    # Seleciona aleatoriamente um valor de fitness
    valor_selecionado = random.uniform(0, soma_fitness)
    acumulado = 0.0

    pai1 = None
    pai2 = None

    for individuo, fitness in populacao_fitness:
        acumulado += fitness
        if acumulado >= valor_selecionado and pai1 is None:
            pai1 = individuo

    # Seleciona o segundo pai de forma semelhante ao primeiro, garantindo que sejam diferentes
    while True:
        valor_selecionado = random.uniform(0, soma_fitness)
        acumulado = 0.0

        for individuo, fitness in populacao_fitness:
            acumulado += fitness
            if acumulado >= valor_selecionado and individuo != pai1:
                pai2 = individuo
                return pai1, pai2  # Retorna os pais selecionados

    return pai1, pai2  # Caso não encontre um segundo pai válido, retorna None para ambos

def metodo_selecao_rank(populacao_fitness):
    populacao_ordenada = sorted(populacao_fitness[:10], key=lambda x: x[1])
    ranks = list(range(1, len(populacao_ordenada) + 1))
    total_ranks = sum(ranks)
    pick1 = random.uniform(0, total_ranks)
    pick2 = random.uniform(0, total_ranks)

    current = 0
    for rank, (individuo, _) in zip(ranks, populacao_ordenada):
        current += rank
        if current > pick1:
            pai1 = individuo
            break

    current = 0
    for rank, (individuo, _) in zip(ranks, populacao_ordenada):
        current += rank
        if current > pick2:
            pai2 = individuo
            break

    return pai1, pai2

def metodo_selecao_elitismo(populacao_fitness):
    populacao_ordenada = sorted(populacao_fitness, key=lambda x: x[1])
    pai1 = populacao_ordenada[0][0]
    pai2 = populacao_ordenada[1][0]
    return pai1, pai2

def metodo_selecao_truncamento(populacao_fitness):
    porcentagem = 0.5
    n_selecionados = int(len(populacao_fitness) * porcentagem)
    populacao_truncada = populacao_fitness[:n_selecionados]
    pai1_fitness, pai2_fitness = random.choices(populacao_truncada, k=2)
    pai1 = pai1_fitness[0]
    pai2 = pai2_fitness[0]
    return pai1, pai2