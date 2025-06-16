#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import streamlit as st
import plotly.express as px

# Configurações da página
st.set_page_config(
    page_title="Radar Legislativo",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Carregar DataFrame
df = pd.read_csv("pls_2000_2025_unificado_com_tema_corrigido_final-gpt4o.csv")

# Renomear tema_nova para tema
if 'tema_nova' in df.columns:
    df.rename(columns={'tema_nova': 'tema'}, inplace=True)

if 'status_final' in df.columns:
    df['status_final'] = df['status_final'].fillna("Desconhecido")


# Corrigir possíveis NaN e garantir string nos filtros
df['autor'] = df['autor'].fillna("Desconhecido").astype(str)
df['tema'] = df['tema'].fillna("Sem tema").astype(str)
df['ano'] = df['ano'].astype(str)

# --------- Agrupar temas nanicos em "Outros" ---------
min_proj_por_tema = 30  # Defina o mínimo que você considerar razoável

contagem_temas = df['tema'].value_counts()
temas_principais = contagem_temas[contagem_temas >= min_proj_por_tema].index
df['tema'] = df['tema'].apply(lambda x: x if x in temas_principais else 'Outros')


# Filtros interativos
anos = st.sidebar.multiselect(
    "Ano",
    sorted(df['ano'].unique()),
    default=sorted(df['ano'].unique())
)

temas = st.sidebar.multiselect(
    "Tema",
    sorted(df['tema'].unique()),
    default=sorted(df['tema'].unique())
)

todos_autores = st.sidebar.checkbox("Selecionar todos os autores", value=True)

if todos_autores:
    autores_selecionados = sorted(df['autor'].unique())
else:
    autores_selecionados = st.sidebar.multiselect(
        "Autor",
        options=sorted(df['autor'].unique()),
        help="Digite para filtrar autores"
    )


df_filtro = df[
    df['ano'].isin(anos) &
    df['tema'].isin(temas) &
    df['autor'].isin(autores)
]

st.title("📊 Radar Legislativo: Análise Temática dos Projetos de Lei")
st.markdown(
    """
    > Explore a produção legislativa de maneira visual, filtrando por ano, tema e autor.  
    > Painel desenvolvido com dados abertos da Câmara dos Deputados.
    """
)

# --- Distribuição dos Temas ---
st.subheader("Distribuição dos Temas")
temas_df = df_filtro['tema'].value_counts().reset_index()
temas_df.columns = ['Tema', 'Projetos']
fig = px.bar(
    temas_df,
    x='Tema',
    y='Projetos',
    color='Tema',
    text_auto=True,
    color_discrete_sequence=px.colors.qualitative.Safe,
    title="Projetos por Tema"
)
fig.update_layout(
    showlegend=False,
    xaxis_title=None,
    yaxis_title="Nº de Projetos",
    margin=dict(l=40, r=40, t=40, b=10)
)
st.plotly_chart(fig, use_container_width=True)

# --- Gráfico dos Autores mais Ativos ---
st.subheader("Autores Mais Ativos")
top_autores = (
    df_filtro['autor'].value_counts()
    .head(10)
    .reset_index()
)
top_autores.columns = ['Autor', 'Projetos']

fig2 = px.bar(
    top_autores,
    x='Autor',
    y='Projetos',
    color='Autor',
    text_auto=True,
    color_discrete_sequence=px.colors.qualitative.Prism,
    title="Top 10 Autores"
)
fig2.update_layout(
    showlegend=False,
    xaxis_title=None,
    yaxis_title="Nº de Projetos",
    margin=dict(l=40, r=40, t=40, b=10)
)
st.plotly_chart(fig2, use_container_width=True)


# --- Exibição da Tabela Detalhada ---
st.subheader("Tabela Detalhada dos Projetos")
st.dataframe(
    df_filtro[['ano', 'ementa', 'autor', 'tema', 'status_final']],
    use_container_width=True,
    height=500
)

import base64

def get_table_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="pls_2000_2025.csv">📥 Baixar base filtrada (.csv)</a>'
    return href

st.markdown(get_table_download_link(df_filtro), unsafe_allow_html=True)

# --- Rodapé ---
st.markdown(
    """
    <hr>
    <div style='text-align: right; font-size: 0.85em; color: #888;'>
        Desenvolvido por Narciso Ribeiro e Gabriel Alves &nbsp; | &nbsp; Powered by OpenAI, Streamlit & Plotly
    </div>
    """,
    unsafe_allow_html=True
)



# In[ ]:




