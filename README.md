# Sumário

## Biblioteca de cores

Para salvar a imagem, o OpenCV **exige** valores inteiros entre **0 e 255**.
`uint8` significa **Unsigned Integer de 8 bits** → intervalo **0 a 255**.
Lembrando: o OpenCV usa **BGR** (azul, verde, vermelho), não RGB. Por isso convertemos **RGB → BGR** antes de salvar.

## RBG e sRGB

Em imagens digitais, os valores RGB geralmente não estão em forma linear. Eles passam por uma curva chamada *gama*, que ajusta como o brilho é representado para se aproximar da sensibilidade do olho humano.  
Esse espaço é chamado de *sRGB*. Ele aplica uma curva fixa (gama = ~2.2) para otimizar a visualização e o uso de bits.

O sRGB é o padrão de monitores e arquivos de imagem. Já o RGB linear é utilizado quando precisamos calcular ou misturar luz de forma correta, como em simulações e efeitos.

A **severidade** representa o **quanto queremos simular** da deficiência visual.

A **Matriz da Deficiência** é uma matriz 3×3 estudada e definida por Machado et al., usada para **simular como uma pessoa com daltonismo percebe as cores**, misturando os canais RGB.

Multiplicar a matriz $M_{def}$ por um vetor de cor $[R,G,B]^T$ (em **RGB linear**) gera uma nova cor que representa essa percepção.

A interpolação:$$M(s) = (1 - s)\,I + s\,M_{def}$$

Permite ajustar o **grau** da simulação:

- s=0: visão normal
- s=1: deficiência severa

O fluxo para ajustar a cor na visão de alguém daltônico seria:

1. sRGB → linear
2. M(s)⋅cor
3. linear → sRGB

## Colisão de cores

A colisão de cores será feita em LAB e não RGB. O motivo é porque duas cores numericamente próximas em RGB, não necessariamente as identifica como cores diferentes.
Com a cor em LAB e o DeltaE200 conseguimos medir a diferença númerica das cores.

O algoritmo identificará quando o DeltaE200 for muito baixo entre duas cores. Já que isso indica que uma pessoa com daltonismo enxerga elas praticamente como se fosse a mesma.

Para melhor definição das colisões, não será feito a comparação pixel a pixel, utilizaremos o algoritmo k-means para agrupar as cores em clusters/paletas.

Então será feita a colisão entre os clusters.


## K-means

criteria_type: condição da parada (por iteração, por erro, ou ambos).
max_iter: número máximo de iterações.
epsilon: limite mínimo de mudança entre iterações.
labels: array onde cada posição indica a qual cluster o pixel pertence.

Estamos utilizando o k-means++, já que é um método melhor para escolher os centróides das cores.

Tendo em mente o código:

```python
compactness, labels, cluster_centers = cv2.kmeans(
        points, K=cluster_number, bestLabels=None, criteria=criteria,
        attempts=attempts, flags=cv2.KMEANS_PP_CENTERS
    )
```

Significado dos parâmetros e retornos:

| Parâmetro                     | Significado                                                        |
| ----------------------------- |--------------------------------------------------------------------|
| `points`                      | Dados de entrada (n,2) → cada ponto é [a*, b*].                    |
| `K=k`                         | Número de clusters.                                                |
| `bestLabels=None`             | OpenCV inicializa automaticamente.                                 |
| `criteria`                    | Critério de parada.                                                |
| `attempts`                    | Quantidade de iterações.                                           |
| `flags=cv2.KMEANS_PP_CENTERS` | Método de inicialização dos centróides (k-means++). |

| Retorno           | Significado                                                                |
| ----------------- | -------------------------------------------------------------------------- |
| `compactness`     | Soma das distâncias dos pontos para seus centróides (valor de erro). |
| `labels`          | Rótulo do cluster de cada ponto (valor inteiro entre `0` e `k-1`).         |
| `cluster_centers` | Coordenadas finais dos centróides (k,2).                                   |
