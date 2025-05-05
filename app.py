import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Ciências de Dados - 2025/1")

# Importar a base de dados
dados = pd.read_excel("CST_EDA_2025.xlsx")

# # Criar DataFrame
# df = pd.DataFrame(dados)
#
# # Converter para float e tratar os None como NaN
# df['Avaliação 01'] = pd.to_numeric(df['Avaliação 01'], errors='coerce')
# df['Recuperação 01'] = pd.to_numeric(df['Recuperação 01'], errors='coerce')
#
# # Criar nova coluna com a maior nota entre Avaliação 01 e Recuperação 01
# df['Nota Final'] = df[['Avaliação 01', 'Recuperação 01']].max(axis=1)
#
# # Criar coluna de cor: vermelho se < 6, azul se >= 6
# df['Cor'] = df['Nota Final'].apply(lambda nota: 'red' if nota < 6 else 'blue')
#
# # st.dataframe(df)
#
# # Título do app
# st.title("Gráfico de Notas da Avaliação 01")
#
# # Exibir tabela
# st.dataframe(df[['Nome', 'Nota Final']])
#
# # Criar gráfico de barras com Plotly
# fig = px.bar(
#     df,
#     x='Nome',
#     y='Nota Final',
#     color='Cor',
#     color_discrete_map={'red': 'red', 'blue': 'blue'},
#     title='Nota por Estudante',
#     labels={'Nota Final': 'Nota'}
# )
#
# # Escala fixa e rótulos inclinados
# fig.update_layout(
#     xaxis_tickangle=-45,
#     yaxis=dict(range=[0, 10]),
#     showlegend=False  # Oculta legenda "Cor"
# )
#
# # Exibir gráfico no Streamlit
# st.plotly_chart(fig)
#
# # Calcular a média e desvio padrão das notas
# media = df['Nota Final'].mean()
# desvio = df['Nota Final'].std()
#
# # Mostrar métricas
# st.markdown("### Estatísticas")
# st.write(f"📊 **Média das notas:** {media:.2f}")
# st.write(f"📈 **Desvio padrão:** {desvio:.2f}")
#
# # Arredondar as notas finais (caso tenham decimais) para agrupar por nota
# df['Nota Arredondada'] = df['Nota Final'].round(0)
#
# # Contar a quantidade de alunos por nota arredondada
# notas_contagem = df['Nota Arredondada'].value_counts().sort_index()
# df_notas = notas_contagem.reset_index()
# df_notas.columns = ['Nota', 'Quantidade']
#
# # Criar gráfico de barras com contagem por nota
# fig2 = px.bar(
#     df_notas,
#     x='Nota',
#     y='Quantidade',
#     title='Distribuição de Notas Finais',
#     labels={'Nota': 'Nota Final', 'Quantidade': 'Número de Alunos'}
# )
#
# # Exibir gráfico
# st.plotly_chart(fig2)
#
#
# # Considerar apenas os alunos que têm nota final válida
# df_validos = df[df['Nota Final'].notna()]
#
# total_validos = len(df_validos)
# acima_media = (df_validos['Nota Final'] >= 6).sum()
# abaixo_media = (df_validos['Nota Final'] < 6).sum()
#
# # Cálculo com base no total válido
# st.write(f"✅ Alunos com nota ≥ 6: {acima_media} ({acima_media / total_validos:.1%})")
# st.write(f"❌ Alunos com nota < 6: {abaixo_media} ({abaixo_media / total_validos:.1%})")

df = pd.DataFrame(dados)

# Calcular nota final
df['Nota Final'] = df[['Avaliação 01', 'Recuperação 01']].max(axis=1)

# Criar coluna de cor para gráfico
df['Cor'] = df['Nota Final'].apply(lambda nota: 'red' if nota < 6 else 'blue')

# Painel
st.title("📊 Painel de Desempenho Acadêmico")

st.subheader("📄 Tabela de Notas Finais")
st.dataframe(df[['Nome', 'Avaliação 01', 'Recuperação 01', 'Nota Final']])

# Gráfico 1 - Nota por aluno
st.subheader("📈 Nota Final por Aluno (cores indicam < ou ≥ 6)")
fig1 = px.bar(
    df,
    x='Nome',
    y='Nota Final',
    color='Cor',
    color_discrete_map={'red': 'red', 'blue': 'blue'},
    title='Notas Finais por Estudante',
    labels={'Nota Final': 'Nota'}
)
fig1.update_layout(xaxis_tickangle=-45, yaxis=dict(range=[0, 10]), showlegend=False)
st.plotly_chart(fig1)

# Estatísticas básicas
st.subheader("📊 Estatísticas da Turma")
df_validos = df[df['Nota Final'].notna()]
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
df_ranking = df_validos.sort_values(by='Nota Final', ascending=False)[['Nome', 'Nota Final']]
st.dataframe(df_ranking.reset_index(drop=True))

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

# # Boxplot
# st.subheader("📦 Boxplot das Notas Finais")
# fig3 = px.box(df_validos, y='Nota Final', title='Distribuição das Notas (Boxplot)')
# st.plotly_chart(fig3)

# Verificação de desempenho da turma
st.subheader("📏 Avaliação da Turma")
if media >= 6:
    st.success("🎉 A média da turma está **acima ou igual à média mínima (6.0)**.")
else:
    st.warning("⚠️ A média da turma está **abaixo da média mínima (6.0)**.")
