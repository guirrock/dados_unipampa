import streamlit as st
import pandas as pd
import altair as alt

# Título
st.title("🎓 Painel de Acompanhamento dos Cursos de Graduação")

# Carrega os dados
df = pd.read_csv("dados_transformados.csv")

# FILTROS
st.sidebar.header("Filtros")

cursos = df["Curso"].unique().tolist()
curso_selecionado = st.sidebar.multiselect("Curso", cursos, default=cursos)

anos = sorted(df["Ano_Ingresso"].dropna().unique())
ano_selecionado = st.sidebar.multiselect("Ano de Ingresso", anos, default=anos)

status_opcao = st.sidebar.multiselect("Status do Aluno", ["Ativo", "Evadido"], default=["Ativo", "Evadido"])

# APLICA FILTROS
df_filtros = df[
    (df["Curso"].isin(curso_selecionado)) &
    (df["Ano_Ingresso"].isin(ano_selecionado)) &
    (df["Status"].isin(status_opcao))
]

# GRÁFICO 1 - Quantidade de alunos por período de ingresso
st.subheader("📊 Quantidade de Alunos por Período de Ingresso")

df_ingressos = df_filtros.groupby(["Ano_Ingresso", "Semestre_Ingresso"]).size().reset_index(name="Total")
df_ingressos["Periodo"] = df_ingressos["Ano_Ingresso"].astype(str) + "/" + df_ingressos["Semestre_Ingresso"].astype(str)

chart1 = alt.Chart(df_ingressos).mark_bar().encode(
    x=alt.X("Periodo:N", sort=None),
    y="Total:Q",
    tooltip=["Periodo", "Total"]
).properties(width=700, height=400)

st.altair_chart(chart1)

# GRÁFICO 2 - Taxa de evasão por curso
st.subheader("📉 Taxa de Evasão por Curso")

df_taxa = df_filtros.groupby("Curso")["Status"].value_counts().unstack(fill_value=0)
df_taxa["Taxa Evasao (%)"] = (df_taxa.get("Evadido", 0) / (df_taxa.get("Evadido", 0) + df_taxa.get("Ativo", 0))) * 100
df_taxa = df_taxa.reset_index()

chart2 = alt.Chart(df_taxa).mark_bar().encode(
    x="Curso:N",
    y=alt.Y("Taxa Evasao (%):Q"),
    tooltip=["Curso", "Taxa Evasao (%)"]
).properties(width=700, height=400)

st.altair_chart(chart2)

# GRÁFICO 3 - Tempo médio até evasão
st.subheader("🕒 Tempo Médio até Evasão (em semestres)")

df_tempom = df_filtros[df_filtros["Status"] == "Evadido"].groupby("Curso")["Tempo_ate_evasao"].mean().reset_index()

chart3 = alt.Chart(df_tempom).mark_bar().encode(
    x="Curso:N",
    y=alt.Y("Tempo_ate_evasao:Q", title="Tempo Médio (semestres)"),
    tooltip=["Curso", "Tempo_ate_evasao"]
).properties(width=700, height=400)

st.altair_chart(chart3)

# TABELA FINAL
st.subheader("📋 Tabela de Alunos (com filtros aplicados)")
st.dataframe(df_filtros)

S