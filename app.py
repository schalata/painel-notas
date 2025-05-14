# --------------------------------------------------
# Painel de Desempenho por Prova - Versão 01
# --------------------------------------------------

import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Painel Acadêmico", layout="wide")
st.title("\U0001F4DA Painel de Desempenho por Prova")

# -------------------------
# CURSO → UC → ARQUIVO
# -------------------------
cursos = {
    "Curso Técnico em Informática Integrado ao Ensino Médio": {
        "Algoritmos e Lógica de Programação": "INF_ALP_2025.xlsx"
    },
    "Curso Superior de Tecnologia em Sistemas para Internet": {
        "Estruturas de Dados": "CST_ATP_2025.xlsx"
    },
    "Curso Superior de Tecnologia em Sistemas para Internet": {
        "Estruturas de Dados": "CST_EDA_2025.xlsx"
    }
}

# Sidebar - Escolha do Curso e UC
st.sidebar.header("⚙️ Configurações")
curso_selecionado = st.sidebar.selectbox("Selecione o curso:", list(cursos.keys()))
ucs_disponiveis = cursos[curso_selecionado]
uc_selecionada = st.sidebar.selectbox("Selecione a unidade curricular:", list(ucs_disponiveis.keys()))
uc_selecionada = str(uc_selecionada).strip()
arquivo_excel = ucs_disponiveis[uc_selecionada]

# -------------------------
# Carregamento e processamento
# -------------------------
df = pd.read_excel(arquivo_excel)

# Detecta quais provas estão presentes
provas_disponiveis = []
for i in range(1, 5):
    pi = f"0{i}"
    if f"Avaliação {pi}" in df.columns:
        provas_disponiveis.append(pi)

if not provas_disponiveis:
    st.error("⚠️ Nenhuma prova encontrada na planilha.")
    st.stop()

# Escolha da prova e tipo de exibição
prova = st.sidebar.selectbox("Selecione a prova:", provas_disponiveis)
tipo = st.sidebar.radio("Tipo de nota a exibir:", ("Apenas Avaliação", "Apenas Recuperação", "Apenas Nota Final", "Todas"))

col_av = f"Avaliação {prova}"
col_rec = f"Recuperação {prova}"
col_final = f"Nota Final {prova}"

# Calcula a nota final da prova selecionada
if col_final not in df.columns:
    df[col_final] = df[[col_av, col_rec]].max(axis=1)

# -------------------------
# TABELA DE NOTAS
# -------------------------
st.subheader("📄 Tabela de Notas")
colunas_tabela = ['Nome']
if tipo == "Apenas Avaliação":
    colunas_tabela.append(col_av)
elif tipo == "Apenas Recuperação":
    colunas_tabela.append(col_rec)
elif tipo == "Apenas Nota Final":
    colunas_tabela.append(col_final)
else:
    colunas_tabela += [col_av, col_rec, col_final]

df_tabela = df[colunas_tabela].copy()
df_tabela.index += 1
st.dataframe(df_tabela)

# -------------------------
# GRÁFICOS
# -------------------------
st.subheader("📈 Gráfico de Notas")
if tipo == "Todas":
    df_melt = df[['Nome', col_av, col_rec]].melt(id_vars='Nome', var_name='Tipo', value_name='Nota')
    fig_duplo = px.bar(df_melt, x='Nome', y='Nota', color='Tipo', barmode='group',
                       title=f"Comparativo Avaliação e Recuperação - Prova {prova} ({uc_selecionada})")
    fig_duplo.update_layout(xaxis_tickangle=-90, yaxis=dict(range=[0, 10]))
    st.plotly_chart(fig_duplo, use_container_width=True)

    df_validos = df[df[col_final].notna()].copy()
    df_validos['Cor'] = df_validos[col_final].apply(lambda x: 'blue' if x >= 6 else 'red')
    df_ordenado = df_validos.sort_values(by='Nome')
    fig_final = px.bar(df_ordenado, x='Nome', y=col_final, color='Cor',
                       color_discrete_map={'blue': 'blue', 'red': 'red'},
                       title=f"Nota Final - Prova {prova} ({uc_selecionada})",
                       category_orders={"Nome": sorted(df_ordenado['Nome'].unique())})
    fig_final.update_layout(xaxis_tickangle=-90, yaxis=dict(range=[0, 10]), showlegend=False)
    st.plotly_chart(fig_final, use_container_width=True)
else:
    coluna = col_av if tipo == "Apenas Avaliação" else col_rec if tipo == "Apenas Recuperação" else col_final
    df_validos = df[df[coluna].notna()].copy()
    df_validos['Cor'] = df_validos[coluna].apply(lambda x: 'blue' if x >= 6 else 'red')
    df_ordenado = df_validos.sort_values(by='Nome')
    fig = px.bar(df_ordenado, x='Nome', y=coluna, color='Cor',
                 color_discrete_map={'blue': 'blue', 'red': 'red'},
                 title=f"{coluna} - Prova {prova} ({uc_selecionada})",
                 category_orders={'Nome': sorted(df_ordenado['Nome'].unique())})
    fig.update_layout(xaxis_tickangle=-90, yaxis=dict(range=[0, 10]), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# -------------------------
# AUSENTES
# -------------------------
if tipo == "Apenas Avaliação":
    st.subheader(f"🚫 Alunos que não fizeram a {col_av}")
    ausentes = df[df[col_av].isna()]['Nome']
    if not ausentes.empty:
        for nome in ausentes:
            st.markdown(f"- {nome}")
    else:
        st.success("Todos os alunos fizeram a avaliação.")
elif tipo == "Apenas Recuperação":
    st.subheader(f"🚫 Alunos que não fizeram a {col_rec} (e estão abaixo da média)")
    df_rec = df[df[col_rec].isna()]
    df_filtrados = df_rec[df_rec[col_av] < 10]
    df_abaixo_media = df_filtrados[df_filtrados[col_av] < 6]
    if df_abaixo_media.empty:
        st.success("Não há alunos abaixo da média que faltaram na recuperação.")
    else:
        for nome in df_abaixo_media['Nome']:
            st.markdown(f"- {nome}")

# -------------------------
# ESTATÍSTICAS
# -------------------------
st.subheader("📊 Estatísticas da Turma")
col_estat = col_av if tipo == "Apenas Avaliação" else col_rec if tipo == "Apenas Recuperação" else col_final
df_estat = df[df[col_estat].notna()].copy()
media = df_estat[col_estat].mean()
desvio = df_estat[col_estat].std()
acima = (df_estat[col_estat] >= 6).sum()
abaixo = (df_estat[col_estat] < 6).sum()
total = len(df_estat)

st.write(f"**Média da turma:** {media:.2f}")
st.write(f"**Desvio padrão:** {desvio:.2f}")
if total > 0:
    st.markdown(f"✅ Alunos com nota ≥ 6: **{acima} ({acima / total:.1%})**")
    st.markdown(f"❌ Alunos com nota < 6: **{abaixo} ({abaixo / total:.1%})**")
else:
    st.warning("⚠️ Nenhuma nota válida registrada para esta prova.")

# -------------------------
# RANKING
# -------------------------
st.subheader("🏅 Ranking de Notas")
ranking = df_estat.sort_values(by=col_estat, ascending=False)[['Nome', col_estat]]
ranking.insert(0, "Posição", range(1, len(ranking) + 1))
st.dataframe(ranking)

# -------------------------
# DISTRIBUIÇÃO DAS NOTAS
# -------------------------
st.subheader(f"📊 Distribuição das Notas - {col_estat}")
df_distrib = df[df[col_estat].notna()].copy()
df_distrib['Nota Arredondada'] = df_distrib[col_estat].round(0)
notas_possiveis = pd.Series(range(0, 11), name="Nota")
frequencia = df_distrib['Nota Arredondada'].value_counts().sort_index()
df_freq = pd.DataFrame({'Nota': frequencia.index, 'Quantidade': frequencia.values})
df_freq = notas_possiveis.to_frame().merge(df_freq, on='Nota', how='left').fillna(0)
df_freq['Quantidade'] = df_freq['Quantidade'].astype(int)

fig_dist = px.bar(df_freq, x='Nota', y='Quantidade',
                  title=f"Distribuição das Notas - {col_estat} - Prova {prova}",
                  labels={'Nota': 'Nota', 'Quantidade': 'Número de Alunos'},
                  width=900)
fig_dist.update_traces(width=0.6)
fig_dist.update_layout(
    xaxis=dict(tickmode='linear', tick0=0, dtick=1, range=[-0.5, 10.5]),
    bargap=0.2
)
st.plotly_chart(fig_dist, use_container_width=True)