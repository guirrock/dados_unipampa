import streamlit as st
import pandas as pd
import altair as alt

# Título
st.title("🎓 Painel de Dados dos Cursos de Graduação")

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
st.subheader("📊 Alunos por Período de Ingresso")

df_ingressos = df_filtros.groupby(["Ano_Ingresso", "Semestre_Ingresso"]).size().reset_index(name="Total")
#df_ingressos = df_ingressos[df_ingressos["Ano_Ingresso"] >= 2014]  # 👈 Filtra apenas anos de 2014 em diante
df_ingressos["Periodo"] = df_ingressos["Ano_Ingresso"].astype(str) + "/" + df_ingressos["Semestre_Ingresso"].astype(str)

chart1 = alt.Chart(df_ingressos).mark_bar().encode(
    x=alt.X("Periodo:N", sort=None, title="Período de Ingresso"),
    y=alt.Y("Total:Q", title="Número de Alunos"),
    tooltip=["Periodo", "Total"]
).properties(width=700, height=400)

st.altair_chart(chart1)

# GRÁFICO 2 - Distribuição de Status por Curso
st.subheader("📘 Distribuição de Status por Curso")

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
st.subheader("📈 Evolução Anual: Diplomados e Desistentes")

# Considera apenas os que têm data de evasão (saída)
df_saida_ano = df[df["Status"].isin(["Diplomado", "Desistente"])].copy()
df_saida_ano["Ano_Evento"] = df_saida_ano["Periodo Evasao"].str.split("/").str[0].astype("Int64")

evolucao_saida = df_saida_ano.groupby(["Ano_Evento", "Status"]).size().reset_index(name="Total")

chart6 = alt.Chart(evolucao_saida).mark_line(point=True).encode(
    x=alt.X("Ano_Evento:O", title="Ano"),
    y=alt.Y("Total:Q", title="Número de Alunos"),
    color="Status:N",
    tooltip=["Ano_Evento", "Status", "Total"]
).properties(width=700, height=400)

st.altair_chart(chart6)



# GRÁFICO 9 - Desistências por Ano
st.subheader("🚪 Desistências por Ano e Curso")

df_evasoes = df_filtros[df_filtros["Status"] == "Desistente"].copy()
df_evasoes["Ano_Evasao"] = df_evasoes["Periodo Evasao"].str.split("/").str[0].astype("Int64")
df_evasoes = df_evasoes[df_evasoes["Ano_Evasao"] >= 2006]  # Se quiser restringir a partir de um ano

evasoes_por_ano = df_evasoes.groupby(["Curso", "Ano_Evasao"]).size().reset_index(name="Desistências")

chart9 = alt.Chart(evasoes_por_ano).mark_line(point=True).encode(
    x=alt.X("Ano_Evasao:O", title="Ano"),
    y=alt.Y("Desistências:Q", title="Número de Desistências"),
    color="Curso:N",
    tooltip=["Curso", "Ano_Evasao", "Desistências"]
).properties(width=700, height=400)
st.altair_chart(chart9)

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


