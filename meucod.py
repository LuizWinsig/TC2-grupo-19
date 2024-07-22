from typing import List, Tuple

import numpy as np
import pygame
import random
from pygame.locals import *
import random
import itertools
import pygame


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

            #print (f"Armazéns: {itens_por_armazem} - Rota: {rota_a_percorrer} - Veículos: {quantidade_veiculos} - Capacidade: {capacidade_veiculo}")

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

    
def metodo_selecao_aleatorio(populacao_fitness):
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



# Constantes e dados do problema
WIDTH, HEIGHT = 800, 600
TAMANHO_POPULACAO = 500
TOTAL_GERACOES = 1000
CAPACIDADE_MAXIMA = 50
MAXIMO_VEICULOS = 10
PROBABILIDADE_MUTACAO = 0.7

PERCENTUAL_MARGEM_TELA = 0.07  # 7% de margem
margin_x = int(WIDTH * PERCENTUAL_MARGEM_TELA)
margin_y = int(HEIGHT * PERCENTUAL_MARGEM_TELA)

NOMES_CIDADES = ["Tokyo", "New York", "Paris", "Berlim", "Roma", "Pequim", "Madrid", "Washington", "Brasilia", "Montevideo"]
LOCAL_CIDADES = [(random.randint(margin_x, WIDTH - margin_x), random.randint(margin_y, HEIGHT - margin_y - 100)) for _ in range(len(NOMES_CIDADES))]
ESTOQUE_MINIMO_CIDADES = [7000, 4200, 3500, 2500, 5000, 6000, 3000, 2500, 1800, 4200]

# Inicializa a tela do Pygame
screen = init_screen(WIDTH, HEIGHT, "Distribuição de carga em armazéns - GA")

#armazens = [Armazem(localizacao, nome_cidade, estoque) for localizacao, nome_cidade, estoque in zip(LOCAL_CIDADES, NOMES_CIDADES, ESTOQUE_MINIMO_CIDADES)]

armazens = []
for local_cidade, nome_cidade, estoque in zip(LOCAL_CIDADES, NOMES_CIDADES, ESTOQUE_MINIMO_CIDADES):
    armazem = Armazem(local_cidade, nome_cidade, estoque)
    armazens.append(armazem)

# Cálculo da matriz de distâncias
dist_matrix = calcular_matriz_distancias(LOCAL_CIDADES)

random.seed(34)  # Valor inicial usado para inicializar um gerador de números aleatórios

def main(screen):
    geracao = gerar_populacao(LOCAL_CIDADES, MAXIMO_VEICULOS, CAPACIDADE_MAXIMA, TAMANHO_POPULACAO)

    contador_geracao = itertools.count(start=1)

    # Mapeamento dos métodos de seleção de pais
    metodos_selecao = {
        1: metodo_selecao_aleatorio,
        2: metodo_selecao_torneio,
        3: metodo_selecao_roleta,
        4: metodo_selecao_rank,
        5: metodo_selecao_elitismo,
        6: metodo_selecao_truncamento,
    }

    melhor_individuo_geral = None
    melhor_tempo_geral = None

    for geracao_atual in range(TOTAL_GERACOES):
        clock = pygame.time.Clock()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        populacao_fitness = []

        for individuo in geracao:
            fitness = individuo.calcular_fitness(ESTOQUE_MINIMO_CIDADES, dist_matrix)
            populacao_fitness.append((individuo, fitness))
            
        populacao_fitness = sorted(populacao_fitness, key=lambda x: x[1])
        melhor_individuo, melhor_tempo = populacao_fitness[0]

        clock.tick(30)
        #print(f"Geração: {contador_geracao} Melhor indivíduo: {melhor_individuo} Melhor tempo: {melhor_tempo}")

        melhor_individuo_geral = melhor_individuo
        melhor_tempo_geral = melhor_tempo

        # Chama a função para desenhar as rotas
        desenhar_rotas(screen, melhor_individuo_geral.rota, armazens)
        desenhar_info(screen, geracao_atual + 1, melhor_tempo_geral, melhor_individuo_geral)
        
        nova_geracao = []

        nova_geracao.append(melhor_individuo)  # Elitismo - nova geração começa com o melhor indivíduo

        while len(nova_geracao) < (TAMANHO_POPULACAO / 10):  # 10% da nova geração é filha dos 10 melhores indivíduos da geração anterior
            metodo = random.randint(1, len(metodos_selecao))  # Gera um número aleatório baseado no tamanho do dicionário de seleção de pais

            pai1, pai2 = metodos_selecao[metodo](populacao_fitness)

            filho = order_crossover(pai1, pai2)

            filho = mutate(filho, PROBABILIDADE_MUTACAO)

            nova_geracao.append(filho)

        restante = TAMANHO_POPULACAO - len(nova_geracao)

        nova_geracao.extend(gerar_populacao(LOCAL_CIDADES, MAXIMO_VEICULOS, CAPACIDADE_MAXIMA, restante))  # Preenche o restante da nova geração com indivíduos aleatórios

        geracao = nova_geracao
        numero_geracao = next(contador_geracao)

    # Mantém a tela aberta depois de completar a execução
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        clock.tick(30)

if __name__ == "__main__":
    main(screen)
