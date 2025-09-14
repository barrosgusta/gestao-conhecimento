# converter.py
import pandas as pd
import os


def converter_excel_para_parquet(caminho_arquivo):
    """
    Converte um arquivo Excel (mesmo que esteja com extensão .parquet) em Parquet real.
    """
    if not os.path.exists(caminho_arquivo):
        print(f"Arquivo não encontrado: {caminho_arquivo}")
        return

    try:
        # Lê como Excel
        df = pd.read_excel(caminho_arquivo)
        # Salva como Parquet real
        df.to_parquet(caminho_arquivo, index=False)
        print(f"Conversão concluída! Arquivo salvo como Parquet real em: {caminho_arquivo}")
    except Exception as e:
        print(f"Erro durante a conversão: {e}")


if __name__ == "__main__":
    caminho = "data/MundoEcommerce.xlsx"  # ajuste se necessário
    converter_excel_para_parquet(caminho)
