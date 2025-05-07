import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Painel Acadêmico", layout="wide")
st.title("📚 Painel de Desempenho por Prova")

# Disciplinas disponíveis
disciplinas = {
    "Algoritmos e Lógica de Programação": "INF_ALP_2025.xlsx",
    "Estruturas de Dados": "CST_EDA_2025.xlsx"
}

# Sidebar de controle
st.sidebar.header("⚙️ Configurações")
disciplina_nome = st.sidebar.selectbox("Selecione a disciplina:", list(disciplinas.keys()))
arquivo_excel = disciplinas[disciplina_nome]

# Carregamento dos dados
df = pd.read_excel(arquivo_excel)

# Cálculo das notas finais para cada prova
for i in range(1, 5):
    pi = f"0{i}"
    df[f"Nota Final {pi}"] = df[[f"Avaliação {pi}", f"Recuperação {pi}"]].max(axis=1)

# Seleção da prova e tipo
prova = st.sidebar.selectbox("Selecione a prova:", ["01", "02", "03", "04"])
tipo = st.sidebar.radio("Tipo de nota a exibir:", ("Apenas Avaliação", "Apenas Recuperação", "Apenas Nota Final", "Todas"))

# Colunas correspondentes
col_av = f"Avaliação {prova}"
col_rec = f"Recuperação {prova}"
col_final = f"Nota Final {prova}"

# Tabela de notas
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
df_tabela.index = df_tabela.index + 1
st.dataframe(df_tabela)

# Gráfico principal
st.subheader("📊 Gráfico de Notas")
if tipo == "Todas":
    df_melt = df[['Nome', col_av, col_rec]].melt(id_vars='Nome', var_name='Tipo', value_name='Nota')
    fig_comparativo = px.bar(df_melt, x='Nome', y='Nota', color='Tipo', barmode='group',
                             title=f"Comparativo Avaliação e Recuperação - Prova {prova} ({disciplina_nome})")
    fig_comparativo.update_layout(xaxis_tickangle=-90, yaxis=dict(range=[0, 10]))
    st.plotly_chart(fig_comparativo, use_container_width=True)

    # Gráfico nota final
    df_final = df[df[col_final].notna()].copy()
    df_final['Cor'] = df_final[col_final].apply(lambda x: 'blue' if x >= 6 else 'red')
    df_final = df_final.sort_values(by='Nome')
    fig_final = px.bar(df_final, x='Nome', y=col_final, color='Cor',
                       color_discrete_map={'blue': 'blue', 'red': 'red'},
                       title=f"Nota Final - Prova {prova} ({disciplina_nome})",
                       category_orders={"Nome": sorted(df_final['Nome'].unique())})
    fig_final.update_layout(xaxis_tickangle=-90, yaxis=dict(range=[0, 10]), showlegend=False)
    st.plotly_chart(fig_final, use_container_width=True)
else:
    coluna = col_av if tipo == "Apenas Avaliação" else col_rec if tipo == "Apenas Recuperação" else col_final
    df_grafico = df[df[coluna].notna()].copy()
    df_grafico['Cor'] = df_grafico[coluna].apply(lambda x: 'blue' if x >= 6 else 'red')
    df_grafico = df_grafico.sort_values(by='Nome')
    fig = px.bar(df_grafico, x='Nome', y=coluna, color='Cor',
                 color_discrete_map={'blue': 'blue', 'red': 'red'},
                 title=f"{coluna} - Prova {prova} ({disciplina_nome})",
                 category_orders={"Nome": sorted(df_grafico['Nome'].unique())})
    fig.update_layout(xaxis_tickangle=-90, yaxis=dict(range=[0, 10]), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# Ausências
if tipo == "Apenas Avaliação":
    st.subheader(f"🚫 Alunos que não fizeram a {col_av}")
    ausentes = df[df[col_av].isna()]['Nome']
    if not ausentes.empty:
        for nome in ausentes:
            st.markdown(f"- {nome}")
    else:
        st.success("Todos os alunos fizeram a avaliação.")
elif tipo == "Apenas Recuperação":
    st.subheader(f"🚫 Alunos que não fizeram a {col_rec}")
    df_rec = df[df[col_rec].isna()]
    if df_rec.empty:
        st.success("Todos os alunos fizeram a recuperação.")
    else:
        for _, row in df_rec.iterrows():
            if pd.notna(row[col_av]) and row[col_av] == 10:
                st.markdown(f"- {row['Nome']} (dispensado - NOTA 10)")
            else:
                st.markdown(f"- {row['Nome']}")

# Estatísticas
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
st.markdown(f"✅ Alunos com nota ≥ 6: **{acima} ({acima / total:.1%})**")
st.markdown(f"❌ Alunos com nota < 6: **{abaixo} ({abaixo / total:.1%})**")

# Ranking
st.subheader("🏅 Ranking de Notas")
ranking = df_estat.sort_values(by=col_estat, ascending=False)[['Nome', col_estat]]
ranking.insert(0, "Posição", range(1, len(ranking) + 1))
st.dataframe(ranking)

# Distribuição das notas com passo 1 e largura igual
st.subheader(f"📊 Distribuição das Notas - {col_estat}")
df_dist = df_estat.copy()
df_dist['Nota Arredondada'] = df_dist[col_estat].round(0)
notas_possiveis = pd.Series(range(0, 11), name="Nota")
frequencia = df_dist['Nota Arredondada'].value_counts().sort_index()
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
