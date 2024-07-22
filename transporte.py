from pygame.locals import *
import random
import itertools
import numpy as np
from typing import Tuple
import pygame
import matplotlib.pyplot as plt
import matplotlib.backends.backend_agg as agg

from funcoes import (
    desenhar_info,
    gerar_populacao,
    calcular_matriz_distancias,
    order_crossover,
    mutate,
    init_screen,
    desenhar_rotas,
    metodo_selecao_aleatorio,
    metodo_selecao_torneio,
    metodo_selecao_roleta,
    metodo_selecao_rank,
<<<<<<< HEAD
    metodo_selecao_elitismo,
    metodo_selecao_truncamento,
    plotar_graficos,
    renderizar_grafico
=======
>>>>>>> 2ac6afb90ca0c573326642fce0f92d41f11d5a5e
)

from tipos import Armazem

# Constantes e dados do problema
WIDTH, HEIGHT = 1000, 800
TAMANHO_POPULACAO = 500
TOTAL_GERACOES = 100
CAPACIDADE_MAXIMA = 50
MAXIMO_VEICULOS = 10
<<<<<<< HEAD
PROBABILIDADE_MUTACAO = 0.2
=======
PROBABILIDADE_MUTACAO = 0.7
METODO_SELECAO = 1
>>>>>>> 2ac6afb90ca0c573326642fce0f92d41f11d5a5e

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
    lista_geracao = []
    tempos_por_geracao= []
    contador_geracao = itertools.count(start=1)

    # Mapeamento dos métodos de seleção de pais
    metodos_selecao = {
        1: metodo_selecao_aleatorio,
        2: metodo_selecao_torneio,
        3: metodo_selecao_roleta,
        4: metodo_selecao_rank,
    }

    melhor_individuo_geral = None
    melhor_tempo_geral = None

    for geracao_atual in range(TOTAL_GERACOES):
        lista_geracao.append(geracao_atual)
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
        tempos_por_geracao.append(melhor_tempo)

        clock.tick(30)
        #print(f"Geração: {contador_geracao} Melhor indivíduo: {melhor_individuo} Melhor tempo: {melhor_tempo}")

        melhor_individuo_geral = melhor_individuo
        melhor_tempo_geral = melhor_tempo
        metodo_selecao_escolhido = metodos_selecao[METODO_SELECAO].__name__
        
        # Chama a função para desenhar as rotas
        desenhar_rotas(screen, melhor_individuo_geral.rota, armazens)
<<<<<<< HEAD
        desenhar_info(screen, geracao_atual + 1, melhor_tempo_geral, melhor_individuo_geral)
        plotar_graficos(range(1, len(lista_geracao) + 1), tempos_por_geracao)
        renderizar_grafico(screen, plt.gcf(), (6 *WIDTH/10, 8*HEIGHT/10 - margin_y),380, 200)

=======
        desenhar_info(screen, geracao_atual + 1, melhor_tempo_geral, melhor_individuo_geral, metodo_selecao_escolhido)
        
>>>>>>> 2ac6afb90ca0c573326642fce0f92d41f11d5a5e
        nova_geracao = []

        #nova_geracao.append(melhor_individuo)  # Elitismo - novaV geração começa com o melhor indivíduo

        while len(nova_geracao) < (TAMANHO_POPULACAO / 10):  # 10% da nova geração é filha dos 10 melhores indivíduos da geração anterior
<<<<<<< HEAD
            metodo = random.randint(1, len(metodos_selecao))  # Gera um número aleatório baseado no tamanho do dicionário de seleção de pais
           # print(f"Método de seleção: {metodo}")
            pai1, pai2 = metodos_selecao[metodo](populacao_fitness)
=======
            
            pai1, pai2 = metodos_selecao[METODO_SELECAO](populacao_fitness)
>>>>>>> 2ac6afb90ca0c573326642fce0f92d41f11d5a5e

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
