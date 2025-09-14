# ui.py
import streamlit as st

from exploratoria import (
    grafico_distribuicao,
    grafico_categorico,
    grafico_boxplot,
    grafico_kde,
    grafico_missing,
    grafico_correlacao,
)
from function import load_database
from ui_helpers import select_with_tooltip

# Try to import dimensional model utilities
try:
    from modelagem import load_star_schema
except Exception:  # pragma: no cover
    load_star_schema = None  # type: ignore

# Configuração da página
st.set_page_config(page_title="Mundo Ecommerce - Análise", layout="wide")

st.title("📊 Análise Exploratória - MundoEcommerce")

# Sidebar: seleção do modo de dados
mode = st.sidebar.radio(
    "Fonte de Dados",
    options=["Dados Brutos", "Modelo Dimensional"],
    help="Escolha analisar diretamente a base original ou o modelo estrela (fato + dimensões).",
)

# Carregar base bruta sempre (usa em ambos os modos para descrições)
df_raw = load_database()

# Mapeamento de descrições em Português para exibir na UI
column_descriptions_pt = {
    "Order ID": "Identificador do pedido. Pode ser usado como chave única para transações.",
    "Order Date": "Data em que o pedido foi realizado. Útil para análises temporais e sazonalidade.",
    "Shipping Date": "Data em que o pedido foi enviado. Serve para calcular tempo de processamento/entrega.",
    "Aging": "Tempo (em dias) entre pedido e entrega ou classificação de envelhecimento.",
    "Ship Mode": "Modalidade de envio (ex.: First Class, Same Day).",
    "Product Category": "Categoria principal do produto (ex.: Eletrônicos, Moda, etc.).",
    "Product": "Nome ou subcategoria do produto vendido.",
    "Sales": "Valor de vendas associado ao item/pedido. Verificar unidade/monetária.",
    "Quantity": "Quantidade de unidades vendidas no item/pedido.",
    "Discount": "Desconto aplicado (proporção ou valor, conforme a base).",
    "Profit": "Lucro associado ao item/pedido (valor monetário).",
    "Shipping Cost": "Custo de envio do pedido (valor monetário).",
    "Order Priority": "Prioridade do pedido (ex.: Low, Medium, High, Critical).",
    "Customer ID": "Identificador do cliente. Pode ser usado para agrupar pedidos por cliente.",
    "Customer Name": "Nome do cliente.",
    "Segment": "Segmento do cliente (ex.: Consumer, Corporate, Home Office).",
    "City": "Cidade do cliente/entrega.",
    "State": "Estado/província do cliente/entrega.",
    "Country": "País do cliente/entrega.",
    "Region": "Região geográfica (agrupamento alto nível).",
}

# --------------------- MODO: MODELO DIMENSIONAL ---------------------
if mode == "Modelo Dimensional":
    st.subheader("🔷 Modelo Dimensional (Star Schema)")
    if load_star_schema is None:
        st.error("Função load_star_schema indisponível. Verifique modelagem.py.")
        st.stop()
    with st.spinner("Carregando modelo dimensional (ou gerando se ausente)..."):
        star = load_star_schema()
    fact = star["fact_sales"]

    # Mostrar overview das tabelas
    with st.expander("Tabelas do Modelo", expanded=False):
        for name, table in star.items():
            st.write(f"{name} -> {table.shape[0]} linhas / {table.shape[1]} colunas")

    st.markdown("Selecione uma dimensão e uma métrica para análise agregada.")

    # Construir catálogo de atributos dimensionais
    dim_attr_catalog = {}
    for dim_name, dim_df in star.items():
        if dim_name.startswith("dim_"):
            # filtrar só colunas não chave numérica
            key_cols = [c for c in dim_df.columns if c.lower().endswith("key")]
            for col in dim_df.columns:
                if col not in key_cols:
                    dim_attr_catalog[f"{dim_name}.{col}"] = (dim_name, col)

    # Métricas disponíveis
    measure_cols = [c for c in ["Sales", "Quantity", "Discount", "Profit", "ShippingCost", "Aging"] if
                    c in fact.columns]

    col_sel1, col_sel2, col_sel3 = st.columns([3, 3, 2])
    selected_attr = col_sel1.selectbox("Atributo de Dimensão", options=sorted(dim_attr_catalog.keys()))
    selected_measure = col_sel2.selectbox("Métrica", options=measure_cols, index=0)
    agg_func = col_sel3.selectbox("Agregação", options=["sum", "mean", "median"], index=0)

    dim_table_name, dim_col = dim_attr_catalog[selected_attr]
    dim_table = star[dim_table_name]

    # Descobrir nome da chave para join com fato
    join_key_candidates = [c for c in dim_table.columns if c.lower().endswith("key")]
    if not join_key_candidates:
        st.error("Não foi possível identificar a chave da dimensão.")
        st.stop()
    dim_key = join_key_candidates[0]

    # Identificar FK correspondente no fato (mesmo nome)
    if dim_key not in fact.columns:
        st.error(f"Fato não possui chave {dim_key} para junção.")
        st.stop()

    # Join e agregação
    df_join = fact[[dim_key, selected_measure]].merge(dim_table[[dim_key, dim_col]], on=dim_key, how="left")
    # Agrupar
    grouped = df_join.groupby(dim_col, dropna=False)[selected_measure]
    if agg_func == "sum":
        agg_df = grouped.sum().reset_index()
    elif agg_func == "mean":
        agg_df = grouped.mean().reset_index()
    else:
        agg_df = grouped.median().reset_index()

    agg_df = agg_df.sort_values(selected_measure, ascending=False).head(30)

    st.subheader("Resultado Agregado")
    st.dataframe(agg_df)

    # Visualização simples (barra)
    try:
        import altair as alt

        chart = alt.Chart(agg_df).mark_bar().encode(
            x=alt.X(f"{selected_measure}:Q", title=selected_measure),
            y=alt.Y(f"{dim_col}:N", sort='-x', title=dim_col),
            tooltip=[dim_col, selected_measure]
        ).properties(height=500)
        st.altair_chart(chart, use_container_width=True)
    except Exception:
        st.bar_chart(agg_df.set_index(dim_col)[selected_measure])

    st.info("Use a aba lateral para voltar aos dados brutos.")
    st.stop()

# --------------------- MODO: DADOS BRUTOS ---------------------

# Visão geral
df = df_raw
st.subheader("Visão Geral dos Dados")
st.write("Dimensão da base:", df.shape)
st.dataframe(df.head())

# Estatísticas
st.subheader("Informações Estatísticas")
st.write(df.describe(include="all"))

# Tipos de colunas
num_cols = df.select_dtypes(include=["number"]).columns.tolist()
cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

# Mostrar valores ausentes (se existirem)
missing_total = df.isna().sum()
if (missing_total > 0).any():
    st.subheader("Valores Ausentes por Coluna")
    fig_miss = grafico_missing(df)
    st.pyplot(fig_miss)

# Correlação (se houver pelo menos 2 numéricas)
if len(num_cols) >= 2:
    st.subheader("Correlação entre Variáveis Numéricas")
    fig_corr = grafico_correlacao(df)
    st.pyplot(fig_corr)

TOP_N = 10

# Distribuição numérica
if num_cols:
    st.subheader("Distribuição de Variáveis Numéricas")
    num_col = select_with_tooltip(
        "Variável numérica",
        options=num_cols,
        key="sel_num_col",
        get_description=lambda c: column_descriptions_pt.get(c, None),
    )
    stats = df[num_col].describe()
    st.write(
        f"Mínimo: {stats['min']:.2f} | Máximo: {stats['max']:.2f} | Média: {stats['mean']:.2f} | Mediana: {df[num_col].median():.2f} | Std: {stats['std']:.2f}"
    )
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.caption("Histograma + KDE")
        st.pyplot(grafico_distribuicao(df, num_col))
    with col_b:
        st.caption("Boxplot")
        st.pyplot(grafico_boxplot(df, num_col))
    with col_c:
        st.caption("Densidade (KDE)")
        st.pyplot(grafico_kde(df, num_col))
else:
    st.info("Nenhuma coluna numérica detectada na base.")

# Frequência categórica
if cat_cols:
    st.subheader("Frequência de Variáveis Categóricas")
    cat_col = select_with_tooltip(
        "Variável categórica",
        options=cat_cols,
        key="sel_cat_col",
        get_description=lambda c: column_descriptions_pt.get(c, None),
    )
    desc = column_descriptions_pt.get(cat_col, "Descrição não disponível para esta coluna.")
    st.markdown(f"**Descrição:** {desc}")
    nunique = int(df[cat_col].nunique())
    mode_val = df[cat_col].mode(dropna=True)[0] if not df[cat_col].dropna().empty else None
    st.write(f"Categorias únicas: {nunique} | Mais frequente: {mode_val}")
    st.pyplot(grafico_categorico(df, cat_col, top_n=TOP_N))
else:
    st.info("Nenhuma coluna categórica detectada na base.")

st.success("✅ Análise concluída")
