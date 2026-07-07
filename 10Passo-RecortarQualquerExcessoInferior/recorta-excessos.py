from PIL import Image
import os
import shutil

def encontrar_borda_inferior(imagem, cor_alvo=(64, 193, 243), tolerancia=15):
    """
    Encontra a borda azul descrita (4px azul, 4px branco, 4px azul) de baixo para cima
    Retorna a posição Y onde deve ser feito o corte (acima da borda) ou None se não encontrar
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    # Percorre a imagem de baixo para cima
    for y in range(altura - 1, 15, -1):  # Começa do fundo, precisa de pelo menos 12 pixels
        # Verifica o padrão da borda: 4px azul, 4px branco, 4px azul
        borda_encontrada = True
        
        # Verifica os 4 pixels azuis inferiores (y-11 até y-8)
        for dy in range(4):
            pixel_y = y - 11 + dy
            if pixel_y < 0:
                borda_encontrada = False
                break
                
            pixel = pixels[largura // 2, pixel_y]
            if len(pixel) == 4:  # RGBA
                r, g, b, a = pixel
            else:  # RGB
                r, g, b = pixel[:3]
            
            # Verifica se é azul (dentro da tolerância)
            if (abs(r - cor_alvo[0]) > tolerancia or 
                abs(g - cor_alvo[1]) > tolerancia or 
                abs(b - cor_alvo[2]) > tolerancia):
                borda_encontrada = False
                break
        
        if not borda_encontrada:
            continue
            
        # Verifica os 4 pixels brancos do meio (y-7 até y-4)
        for dy in range(4):
            pixel_y = y - 7 + dy
            pixel = pixels[largura // 2, pixel_y]
            if len(pixel) == 4:  # RGBA
                r, g, b, a = pixel
            else:  # RGB
                r, g, b = pixel[:3]
            
            # Verifica se é branco (dentro da tolerância)
            if (abs(r - 255) > tolerancia or 
                abs(g - 255) > tolerancia or 
                abs(b - 255) > tolerancia):
                borda_encontrada = False
                break
        
        if not borda_encontrada:
            continue
            
        # Verifica os 4 pixels azuis superiores (y-3 até y)
        for dy in range(4):
            pixel_y = y - 3 + dy
            pixel = pixels[largura // 2, pixel_y]
            if len(pixel) == 4:  # RGBA
                r, g, b, a = pixel
            else:  # RGB
                r, g, b = pixel[:3]
            
            # Verifica se é azul (dentro da tolerância)
            if (abs(r - cor_alvo[0]) > tolerancia or 
                abs(g - cor_alvo[1]) > tolerancia or 
                abs(b - cor_alvo[2]) > tolerancia):
                borda_encontrada = False
                break
        
        if borda_encontrada:
            print(f"Borda encontrada! Cortando na posição y={y-11}")
            return y - 11  # Retorna a posição acima da borda completa
    
    return None

def processar_imagens(pasta_origem, pasta_destino, cor_alvo=(64, 193, 243)):
    """
    Processa todas as imagens da pasta origem, recortando as que têm borda azul inferior
    e copiando todas para a pasta destino
    """
    # Cria a pasta de destino se não existir
    os.makedirs(pasta_destino, exist_ok=True)
    
    # Lista todos os arquivos da pasta origem
    arquivos = [f for f in os.listdir(pasta_origem) 
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]
    
    print(f"Encontrados {len(arquivos)} arquivos para processar")
    
    for arquivo in arquivos:
        caminho_origem = os.path.join(pasta_origem, arquivo)
        caminho_destino = os.path.join(pasta_destino, arquivo)
        
        try:
            # Abre a imagem
            with Image.open(caminho_origem) as imagem:
                print(f"\nProcessando: {arquivo} ({imagem.width}x{imagem.height})")
                
                # Procura pela borda inferior
                posicao_corte = encontrar_borda_inferior(imagem, cor_alvo)
                
                if posicao_corte is not None and posicao_corte > 0:
                    # Se encontrou a borda, recorta a imagem
                    area_corte = (0, 0, imagem.width, posicao_corte)
                    imagem_recortada = imagem.crop(area_corte)
                    imagem_recortada.save(caminho_destino)
                    print(f"✓ Imagem recortada: {imagem_recortada.width}x{imagem_recortada.height}")
                else:
                    # Se não encontrou borda, copia a imagem original
                    shutil.copy2(caminho_origem, caminho_destino)
                    print(f"✓ Imagem mantida original (sem borda detectada)")
                    
        except Exception as e:
            print(f"✗ Erro ao processar {arquivo}: {e}")
            # Tenta copiar o arquivo mesmo com erro
            try:
                shutil.copy2(caminho_origem, caminho_destino)
                print(f"✓ Arquivo copiado mesmo com erro")
            except:
                print(f"✗ Não foi possível copiar o arquivo")

# Função principal
if __name__ == "__main__":
    # Configurações
    pasta_origem = "../10Passo-RecortarQualquerExcessoInferior"
    pasta_destino = "."
    cor_azul = (64, 193, 243)  # RGB para #40c1f3
    
    print("Iniciando processamento de imagens...")
    print(f"Pasta origem: {pasta_origem}")
    print(f"Pasta destino: {pasta_destino}")
    print(f"Cor alvo: RGB{cor_azul} (#40c1f3)")
    
    # Verifica se a pasta origem existe
    if not os.path.exists(pasta_origem):
        print(f"Erro: A pasta '{pasta_origem}' não existe!")
        exit(1)
    
    # Executa o processamento
    processar_imagens(pasta_origem, pasta_destino, cor_azul)
    
    print("\n" + "="*50)
    print("Processamento concluído!")
    print(f"Todas as imagens foram salvas em: {pasta_destino}")