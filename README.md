# Gestão do Conhecimento - Como executar

Este repositório contém uma pequena aplicação Python com interface em Streamlit e módulos para
conversão/exploração/modelagem de dados.

Pré-requisitos

- Python 3.8+ (recomendado 3.10/3.11/3.13 conforme seu ambiente)
- Git (opcional)
- Acesso aos arquivos em `data/` (já incluídos no projeto: parquet)

Instalação (recomendada em ambiente virtual)

1. Criar e ativar um venv (exemplo macOS / Linux):
   python -m venv .venv
   source .venv/bin/activate

   Windows (PowerShell):
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

2. Instalar dependências:
   pip install -r requirements.txt

3. Se quiser “congelar” as dependências atuais:
   pip freeze > requirements.txt

Executando a interface Streamlit

1. No diretório do projeto, rode:
   streamlit run ui.py

2. O Streamlit abrirá no navegador (normalmente http://localhost:8501). Se quiser usar uma porta diferente:
   streamlit run ui.py --server.port 8502

Execução de outros scripts

- Alguns módulos utilitários ou scripts podem ser executados diretamente, por exemplo:
  python aplicacao.py
  python main.py
  python exploratoria.py

Observações sobre dados

- Os arquivos Parquet ficam em `data/` e em `data/warehouse/` (dim_*.parquet e fact_sales.parquet).
- Certifique-se de ter as dependências para ler parquet (por ex. pyarrow).

Soluções rápidas para erros comuns

- Erro "TypeError: Object of type Timestamp is not JSON serializable": converta datas para string antes de serializar (
  ex.: df['date'] = df['date'].dt.strftime('%Y-%m-%d') ou use .isoformat()).
- Problemas com CSS/HTML no Streamlit: verifique se `st.markdown(..., unsafe_allow_html=True)` está sendo usado
  corretamente.

Dicas de desenvolvimento

- Edite `ui.py` para mudanças na interface e `ui_helpers.py` para componentes/estilos. Para separar lógica, verifique
  `modelagem.py` e `converter.py`.
- Para integrar modelagem dimensional (star schema), a função esperada é `load_star_schema` em `modelagem.py`.

