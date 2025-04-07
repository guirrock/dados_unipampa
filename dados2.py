import streamlit as st
import pandas as pd
import altair as alt

# Título
st.title("🎓 Painel de Acompanhamento dos Cursos de Graduação")

# Carrega os dados
df = pd.read_csv("dados_transformados_atualizados.csv")  # Novo CSV com coluna 'Status' atualizada

# Cria colunas auxiliares se ainda não tiverem sido salvas
if "Ano_Ingresso" not in df.columns:
    df["Ano_Ingresso"] = df["Periodo Ingresso"].str.split("/").str[0].astype(int)
    df["Semestre_Ingresso"] = df["Periodo Ingresso"].str.split("/").str[1].astype(int)

# FILTROS
st.sidebar.header("Filtros")

cursos = df["Curso"].unique().tolist()
curso_selecionado = st.sidebar.multiselect("Curso", cursos, default=cursos)

anos = sorted(df["Ano_Ingresso"].dropna().unique())
ano_selecionado = st.sidebar.multiselect("Ano de Ingresso", anos, default=anos)

status_opcao = st.sidebar.multiselect("Status do Aluno", ["Ativo", "Diplomado", "Desistente"], default=["Ativo", "Diplomado", "Desistente"])

# APLICA FILTROS
df_filtros = df[
    (df["Curso"].isin(curso_selecionado)) &
    (df["Ano_Ingresso"].isin(ano_selecionado)) &
    (df["Status"].isin(status_opcao))
]

# GRÁFICO 1 - Quantidade de alunos por período de ingresso
st.subheader("📊 Quantidade de Alunos por Período de Ingresso  (2014-2025)")

df_ingressos = df_filtros.groupby(["Ano_Ingresso", "Semestre_Ingresso"]).size().reset_index(name="Total")
df_ingressos = df_ingressos[df_ingressos["Ano_Ingresso"] >= 2014]  # 👈 Filtra apenas anos de 2014 em diante
df_ingressos["Periodo"] = df_ingressos["Ano_Ingresso"].astype(str) + "/" + df_ingressos["Semestre_Ingresso"].astype(str)

chart1 = alt.Chart(df_ingressos).mark_bar().encode(
    x=alt.X("Periodo:N", sort=None, title="Período de Ingresso"),
    y=alt.Y("Total:Q", title="Número de Alunos"),
    tooltip=["Periodo", "Total"]
).properties(width=700, height=400)

st.altair_chart(chart1)

# GRÁFICO 2 - Distribuição de Status por Curso
st.subheader("📘 Distribuição de Status por Curso  (2014-2025)")

df_status = df_filtros.groupby(["Curso", "Status"]).size().reset_index(name="Total")

chart2 = alt.Chart(df_status).mark_bar().encode(
    x=alt.X("Curso:N", title="Curso"),
    y=alt.Y("Total:Q", title="Número de Alunos"),
    color="Status:N",
    tooltip=["Curso", "Status", "Total"]
).properties(width=700, height=400)

st.altair_chart(chart2)

# GRÁFICO 3 - Tempo médio até saída (diplomação ou desistência)
st.subheader("🕒 Tempo Médio até Saída (em semestres)")

df_saida = df_filtros[df_filtros["Status"].isin(["Diplomado", "Desistente"])]
df_tempom = df_saida.groupby(["Curso", "Status"])["Tempo_ate_evasao"].mean().reset_index()

chart3 = alt.Chart(df_tempom).mark_bar().encode(
    x="Curso:N",
    y=alt.Y("Tempo_ate_evasao:Q", title="Tempo Médio (semestres)"),
    color="Status:N",
    tooltip=["Curso", "Status", "Tempo_ate_evasao"]
).properties(width=700, height=400)

st.altair_chart(chart3)

# GRÁFICO 4 - Diplomados por Ano
st.subheader("🎓 Diplomados por Ano")

df_diplomados = df_filtros[df_filtros["Status"] == "Diplomado"].copy()
df_diplomados["Ano_Diploma"] = df_diplomados["Periodo Evasao"].str.split("/").str[0].astype("Int64")

df_dipl_ano = df_diplomados.groupby(["Curso", "Ano_Diploma"]).size().reset_index(name="Diplomados")

chart4 = alt.Chart(df_dipl_ano).mark_line(point=True).encode(
    x=alt.X("Ano_Diploma:O", title="Ano"),
    y=alt.Y("Diplomados:Q", title="Número de Diplomados"),
    color="Curso:N",
    tooltip=["Curso", "Ano_Diploma", "Diplomados"]
).properties(width=700, height=400)

st.altair_chart(chart4)

# GRÁFICO 5 - Proporção de Diplomados por Curso
st.subheader("🎯 Proporção de Diplomados por Curso")

df_diplomados = df[df["Status"] == "Diplomado"]
df_totais = df.groupby("Curso")["Matricula"].count().reset_index(name="Total")
df_diplomados_contagem = df_diplomados.groupby("Curso")["Matricula"].count().reset_index(name="Diplomados")

df_proporcao = pd.merge(df_totais, df_diplomados_contagem, on="Curso", how="left").fillna(0)
df_proporcao["Proporcao_Diplomados (%)"] = (df_proporcao["Diplomados"] / df_proporcao["Total"]) * 100

chart5 = alt.Chart(df_proporcao).mark_bar().encode(
    x="Curso:N",
    y=alt.Y("Proporcao_Diplomados (%):Q"),
    tooltip=["Curso", "Proporcao_Diplomados (%)"]
).properties(width=700, height=400)

st.altair_chart(chart5)

# GRÁFICO 6 - Evolução anual: ingressantes, diplomados e evadidos
st.subheader("📈 Evolução Anual: Ingressantes, Diplomados e Evadidos")

df["Ano"] = df["Ano_Ingresso"]

# Filtra apenas anos a partir de 2014
df_evolucao = df[df["Ano"] >= 2014]

evolucao = df_evolucao.groupby(["Ano", "Status"]).size().reset_index(name="Total")
chart6 = alt.Chart(evolucao).mark_line(point=True).encode(
    x="Ano:O",
    y="Total:Q",
    color="Status:N",
    tooltip=["Ano", "Status", "Total"]
).properties(width=700, height=400)

st.altair_chart(chart6)

# GRÁFICO 7 - Tempo médio até diplomação
st.subheader("🎓 Tempo Médio até Diplomação (em semestres)")

df_tempo_diploma = df[df["Status"] == "Diplomado"].groupby("Curso")["Tempo_ate_evasao"].mean().reset_index()
chart7 = alt.Chart(df_tempo_diploma).mark_bar().encode(
    x="Curso:N",
    y=alt.Y("Tempo_ate_evasao:Q", title="Tempo Médio (semestres)"),
    tooltip=["Curso", "Tempo_ate_evasao"]
).properties(width=700, height=400)

st.altair_chart(chart7)

# GRÁFICO 8 - Distribuição por Semestre de Ingresso
st.subheader("🗓️ Distribuição de Ingressantes por Semestre")

df_semestres = df.groupby("Semestre_Ingresso").size().reset_index(name="Total")
chart8 = alt.Chart(df_semestres).mark_bar().encode(
    x=alt.X("Semestre_Ingresso:N", title="Semestre"),
    y=alt.Y("Total:Q", title="Número de Alunos"),
    tooltip=["Semestre_Ingresso", "Total"]
).properties(width=500, height=300)

st.altair_chart(chart8)

# GRÁFICO 9 - Comparativo entre modalidades

st.subheader("🏫 Comparativo entre Modalidades (Integral vs Noturno)")

# Considera apenas os diplomados
df_diplomados = df[df["Status"] == "Diplomado"].copy()

# Extrai Curso Base e Modalidade a partir do nome do curso
df_diplomados["Curso_Base"] = df_diplomados["Curso"].str.extract(r"^(.*?)(?: - .*)?$")[0].str.strip()
df_diplomados["Modalidade"] = df_diplomados["Curso"].str.extract(r"- (INTEGRAL|NOTURNO)$", expand=False)
df_diplomados["Modalidade"] = df_diplomados["Modalidade"].fillna("Única")  # cursos que não têm divisão

# Agrupa por curso base e modalidade
df_mod_grouped = df_diplomados.groupby(["Curso_Base", "Modalidade"]).size().reset_index(name="Total")

chart9 = alt.Chart(df_mod_grouped).mark_bar().encode(
    x=alt.X("Curso_Base:N", title="Curso"),
    y=alt.Y("Total:Q", title="Diplomados"),
    color=alt.Color("Modalidade:N", legend=alt.Legend(title="Modalidade")),
    tooltip=["Curso_Base", "Modalidade", "Total"]
).properties(width=700, height=400)

st.altair_chart(chart9)
