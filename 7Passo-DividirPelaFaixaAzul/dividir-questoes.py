"""
Propósito: Dividir as questões pela faixa azul
Versão ajustada para gerar várias partes e ignorar só partes muito pequenas
"""

from PIL import Image
import os

Image.MAX_IMAGE_PIXELS = None


def converter_cor_gimp_para_rgb(gimp_r, gimp_g, gimp_b):
    r = int((gimp_r / 100) * 255)
    g = int((gimp_g / 100) * 255)
    b = int((gimp_b / 100) * 255)
    return (r, g, b)


def encontrar_faixa_azul(
    imagem,
    cor_alvo=(64, 193, 243),
    tolerancia=15,
    altura_faixa=10
):
    largura, altura = imagem.size
    pixels = imagem.load()

    posicoes_corte = []
    y = 0

    while y < altura - altura_faixa:
        faixa_encontrada = True

        for dy in range(altura_faixa):
            pixel = pixels[largura // 2, y + dy]

            if len(pixel) == 4:
                r, g, b, a = pixel
            else:
                r, g, b = pixel[:3]

            if (
                abs(r - cor_alvo[0]) > tolerancia
                or abs(g - cor_alvo[1]) > tolerancia
                or abs(b - cor_alvo[2]) > tolerancia
            ):
                faixa_encontrada = False
                break

        if faixa_encontrada:
            posicao_corte = y - 13

            if posicao_corte < 0:
                posicao_corte = 0

            if not posicoes_corte or posicao_corte - posicoes_corte[-1] > 50:
                posicoes_corte.append(posicao_corte)
                print(f"Faixa azul encontrada em y={y}, cortando em y={posicao_corte}")

            y += 30
        else:
            y += 1

    return posicoes_corte


def dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_alvo=(64, 193, 243)):
    if not os.path.exists(caminho_imagem):
        print(f"ERRO: arquivo não encontrado: {caminho_imagem}")
        return

    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size

    print(f"Imagem carregada: {largura}x{altura} pixels")

    posicoes_corte = encontrar_faixa_azul(imagem, cor_alvo)

    if not posicoes_corte:
        print("Nenhuma faixa azul encontrada na imagem!")
        return

    print(f"Encontradas {len(posicoes_corte)} faixas azuis para corte")

    os.makedirs(pasta_saida, exist_ok=True)

    posicao_anterior = 0
    contador = 1

    for posicao_corte in posicoes_corte:
        altura_secao = posicao_corte - posicao_anterior

        if altura_secao < 80:
            print(f"Ignorado corte pequeno com {altura_secao}px")
            continue

        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)

        nome_arquivo = f"parte_{contador:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)

        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

        contador += 1
        posicao_anterior = posicao_corte + 10

    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)

        if secao.height >= 80:
            nome_arquivo = f"parte_{contador:03d}.png"
            caminho_completo = os.path.join(pasta_saida, nome_arquivo)

            secao.save(caminho_completo)
            print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

    print("Finalizado.")


if __name__ == "__main__":
    caminho_imagem = "colunas_concatenadas_verticalmente.png"
    pasta_saida = "questoes_colunas"

    cor_azul = converter_cor_gimp_para_rgb(25.1, 75.7, 95.3)

    print(f"Cor convertida: RGB{cor_azul}")

    dividir_imagem_por_faixas(
        caminho_imagem,
        pasta_saida,
        cor_azul
    )

    print("Divisão concluída!")