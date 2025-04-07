import streamlit as st
import pandas as pd
import altair as alt

# Carrega os dados atualizados
df = pd.read_csv("dados_transformados_atualizados.csv")

# Pré-processamento básico
df["Ano_Ingresso"] = df["Periodo Ingresso"].str.split("/").str[0].astype(int)
df["Semestre_Ingresso"] = df["Periodo Ingresso"].str.split("/").str[1].astype(int)

# Filtros
st.sidebar.header("Filtros")
cursos = df["Curso"].unique().tolist()
curso_selecionado = st.sidebar.multiselect("Curso", cursos, default=cursos)

anos = sorted(df["Ano_Ingresso"].dropna().unique())
ano_selecionado = st.sidebar.multiselect("Ano de Ingresso", anos, default=anos)

status_opcao = st.sidebar.multiselect("Status", ["Ativo", "Diplomado", "Desistente"], default=["Ativo", "Diplomado", "Desistente"])

df_filtros = df[
    (df["Curso"].isin(curso_selecionado)) &
    (df["Ano_Ingresso"].isin(ano_selecionado)) &
    (df["Status"].isin(status_opcao))
]

st.title("🎓 Painel de Acompanhamento dos Cursos de Graduação")

# Gráfico 1: Distribuição de status por curso
st.subheader("📊 Distribuição de Status por Curso")
df_status = df_filtros.groupby(["Curso", "Status"]).size().reset_index(name="Total")
chart_status = alt.Chart(df_status).mark_bar().encode(
    x="Curso:N",
    y="Total:Q",
    color="Status:N",
    tooltip=["Curso", "Status", "Total"]
).properties(width=700, height=400)
st.altair_chart(chart_status)

# Gráfico 2: Diplomados por ano
st.subheader("🎓 Número de Diplomados por Ano")
df_diplomados = df_filtros[df_filtros["Status"] == "Diplomado"]
df_diplomados["Ano_Diploma"] = df_diplomados["Periodo Evasao"].str.split("/").str[0].astype("Int64")
df_por_ano = df_diplomados.groupby(["Curso", "Ano_Diploma"]).size().reset_index(name="Diplomados")

chart_diploma = alt.Chart(df_por_ano).mark_line(point=True).encode(
    x="Ano_Diploma:O",
    y="Diplomados:Q",
    color="Curso:N",
    tooltip=["Curso", "Ano_Diploma", "Diplomados"]
).properties(width=700, height=400)

st.altair_chart(chart_diploma)

# Gráfico 3: Tempo médio até diploma ou desistência
st.subheader("🕒 Tempo Médio (em semestres) até Diplomação ou Desistência")
df_tempos = df_filtros[df_filtros["Status"].isin(["Diplomado", "Desistente"])]
df_tempo_medio = df_tempos.groupby(["Curso", "Status"])["Tempo_ate_evasao"].mean().reset_index()

chart_tempo = alt.Chart(df_tempo_medio).mark_bar().encode(
    x="Curso:N",
    y=alt.Y("Tempo_ate_evasao:Q", title="Tempo Médio"),
    color="Status:N",
    tooltip=["Curso", "Status", "Tempo_ate_evasao"]
).properties(width=700, height=400)

st.altair_chart(chart_tempo)

# Tabela final
st.subheader("📋 Dados Detalhados")
st.dataframe(df_filtros)
