import streamlit as st
import pandas as pd
import plotly.express as px

# st.title("Estrutura de Dados - 2025/1")
st.title("DashBoard - Turmas: 2025/1")

# # Importar a base de dados
# # dados = pd.read_excel("CST_EDA_2025.xlsx")
# dados = pd.read_excel("INF_ALP_2025.xlsx")


# Seleção da turma
turma_opcao = st.selectbox(
    "Selecione a turma:",
    ("CST - Estrutura de Dados", "INFO - Algoritmos e Lógica de Programação")
)

# Carregar os dados com base na turma selecionada
if turma_opcao == "CST - Estrutura de Dados":
    arquivo_excel = "CST_EDA_2025.xlsx"
else:
    arquivo_excel = "INF_ALP_2025.xlsx"

# Carregar os dados
dados = pd.read_excel(arquivo_excel)

# Criar dataFrame
df = pd.DataFrame(dados)

# Calcular nota final
df['Nota Final'] = df[['Avaliação 01', 'Recuperação 01']].max(axis=1)

# Criar coluna de cor para gráfico
df['Cor'] = df['Nota Final'].apply(lambda nota: 'red' if nota < 6 else 'blue')

# Painel
st.title("📊 Painel de Desempenho Acadêmico")

st.subheader("📄 Tabela de Notas Finais")
# Para a tabela começar a contar na linha 1 e não 0
df= df.reset_index(drop=True)
df.index = df.index + 1

st.dataframe(df[['Nome', 'Avaliação 01', 'Recuperação 01', 'Nota Final']])

# Ordena o DataFrame por nome
df_ordenado = df.sort_values(by='Nome')

# Alunos que não fizeram nenhuma das provas
st.subheader("🚫 Alunos que não realizaram nenhuma avaliação")

alunos_ausentes = df[df[['Avaliação 01', 'Recuperação 01']].isna().all(axis=1)]

if not alunos_ausentes.empty:
    st.write("**Lista de alunos ausentes:**")
    df_ausentes = alunos_ausentes[['Nome']].reset_index(drop=True)
    df_ausentes.index += 1  # Faz o índice começar de 1
    st.dataframe(df_ausentes)
else:
    st.success("Todos os alunos fizeram pelo menos uma das avaliações.")


# Gráfico 1 - Nota por aluno (com ordem alfabética real)
st.subheader("📈 Nota Final por Aluno")
fig1 = px.bar(
    df_ordenado,
    x='Nome',
    y='Nota Final',
    color='Cor',
    color_discrete_map={'red': 'red', 'blue': 'blue'},
    title='Notas Finais por Estudante',
    labels={'Nota Final': 'Nota'},
    category_orders={'Nome': df_ordenado['Nome'].tolist()}  # <- Força a ordem alfabética no eixo X
)
fig1.update_layout(xaxis_tickangle=-90, yaxis=dict(range=[0, 10]), showlegend=False)
st.plotly_chart(fig1)

# Estatísticas básicas
st.subheader("📊 Estatísticas da Turma")
# df_validos = df[df['Nota Final'].notna()]
df_validos = df[df['Nota Final'].notna()].copy()
media = df_validos['Nota Final'].mean()
desvio = df_validos['Nota Final'].std()

st.write(f"**Média da turma:** {media:.2f}")
st.write(f"**Desvio padrão:** {desvio:.2f}")

# Percentual acima/abaixo da média
acima_media = (df_validos['Nota Final'] >= 6).sum()
abaixo_media = (df_validos['Nota Final'] < 6).sum()
total_validos = len(df_validos)

st.markdown("### ✅❌ Desempenho em relação à média")
st.markdown(f"✅ Alunos com nota ≥ 6: **{acima_media} ({acima_media / total_validos:.1%})**")
st.markdown(f"❌ Alunos com nota < 6: **{abaixo_media} ({abaixo_media / total_validos:.1%})**")

# Ranking
st.subheader("🏅 Ranking de Notas")
# Ordenar por nota decrescente
df_ranking = df_validos.sort_values(by='Nota Final', ascending=False)[['Nome', 'Nota Final']]
# Adicionar a coluna 'Posição' iniciando em 1
df_ranking.insert(0, 'Posição', range(1, len(df_ranking) + 1))
# st.dataframe(df_ranking.reset_index(drop=True))
st.dataframe(df_ranking)

# Gráfico 2 - Distribuição de notas
st.subheader("📊 Distribuição de Notas")
df_validos['Nota Arredondada'] = df_validos['Nota Final'].round(0)
notas_contagem = df_validos['Nota Arredondada'].value_counts().sort_index()
df_nota_freq = notas_contagem.reset_index()
df_nota_freq.columns = ['Nota', 'Quantidade']

fig2 = px.bar(
    df_nota_freq,
    x='Nota',
    y='Quantidade',
    title='Frequência das Notas Finais',
    labels={'Nota': 'Nota Final', 'Quantidade': 'Número de Alunos'}
)
st.plotly_chart(fig2)

# Verificação de desempenho da turma
st.subheader("📏 Avaliação da Turma")
if media >= 6:
    st.success("🎉 A média da turma está **acima ou igual à média mínima (6.0)**.")
else:
    st.warning("⚠️ A média da turma está **abaixo da média mínima (6.0)**.")

if __name__ == 'main':
    app.run_server()