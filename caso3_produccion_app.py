import streamlit as st
import pandas as pd
import plotly.express as px

# ─── CONFIGURACIÓN DE PÁGINA ─────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Producción",
    page_icon="🏭",
    layout="wide"
)

# ─── CARGA DE DATOS ──────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv('caso3_produccion_dataset.csv')
    return df

df = load_data()

# ─── BARRA LATERAL (FILTROS) ─────────────────────────────────────
st.sidebar.header("🔍 Filtros")

# Filtro de Línea
lineas_opciones = ["Todas"] + list(df['linea_produccion'].unique())
linea_sel = st.sidebar.selectbox("Línea de Producción", lineas_opciones)

# Filtro de Turno
turnos_opciones = ["Todos"] + list(df['turno'].unique())
turno_sel = st.sidebar.selectbox("Turno", turnos_opciones)

# Aplicar filtros
df_filtrado = df.copy()
if linea_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado['linea_produccion'] == linea_sel]
if turno_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado['turno'] == turno_sel]

# ─── ENCABEZADO ──────────────────────────────────────────────────
st.title("🏭 Dashboard de Producción Industrial")
st.markdown("---")

# Validar si el filtro deja datos vacíos
if df_filtrado.empty:
    st.warning("⚠️ No hay datos disponibles para la combinación de filtros seleccionada.")
    st.stop()

# ─── SECCIÓN 1: KPIs ─────────────────────────────────────────────
st.subheader("📌 Indicadores Clave (KPIs)")

col1, col2, col3, col4, col5 = st.columns(5)

# Cálculos
efi_prom = df_filtrado['eficiencia_pct'].mean()
def_prom = df_filtrado['tasa_defectos_pct'].mean()
tot_prod = df_filtrado['unidades_producidas'].sum()
costo_tot = df_filtrado['costo_produccion_cop'].sum()
paro_tot = df_filtrado['tiempo_paro_min'].sum()

# Mostrar métricas
col1.metric("Eficiencia Prom.", f"{efi_prom:.2f}%")
col2.metric("Tasa Defectos", f"{def_prom:.2f}%")
col3.metric("U. Producidas", f"{tot_prod:,.0f}")
col4.metric("Costo Producción", f"${costo_tot:,.0f}")
col5.metric("Tiempo Paro", f"{paro_tot:,.0f} min")

st.markdown("---")

# ─── SECCIÓN 2: GRÁFICOS (FILA 1) ────────────────────────────────
colA, colB = st.columns(2)

with colA:
    st.markdown("#### Eficiencia Promedio por Línea")
    efic_linea = df_filtrado.groupby('linea_produccion', as_index=False)['eficiencia_pct'].mean()
    fig1 = px.bar(
        efic_linea.sort_values('eficiencia_pct'),
        y='linea_produccion', 
        x='eficiencia_pct',
        orientation='h',
        color='eficiencia_pct',
        color_continuous_scale='Blues',
        text_auto='.2s'
    )
    fig1.update_layout(height=350, showlegend=False, xaxis_title="Eficiencia (%)", yaxis_title="")
    st.plotly_chart(fig1, width='stretch')

with colB:
    st.markdown("#### Defectos por Turno")
    fig2 = px.violin(
        df_filtrado, 
        x='turno', 
        y='tasa_defectos_pct',
        color='turno', 
        box=True, 
        points='all'
    )
    fig2.update_layout(height=350, showlegend=False, xaxis_title="Turno", yaxis_title="Tasa Defectos (%)")
    st.plotly_chart(fig2, width='stretch')

st.markdown("---")

# ─── SECCIÓN 3: GRÁFICOS (FILA 2) ────────────────────────────────
colC, colD = st.columns(2)

with colC:
    st.markdown("#### Tiempo de Paro por Máquina")
    paro_maq = df_filtrado.groupby('maquina', as_index=False)['tiempo_paro_min'].sum()
    fig3 = px.bar(
        paro_maq.sort_values('tiempo_paro_min'),
        y='maquina', 
        x='tiempo_paro_min',
        orientation='h',
        color='tiempo_paro_min',
        color_continuous_scale='Reds',
        text_auto='.2s'
    )
    fig3.update_layout(height=350, showlegend=False, xaxis_title="Tiempo Paro (min)", yaxis_title="")
    st.plotly_chart(fig3, width='stretch')

with colD:
    st.markdown("#### Temperatura vs Defectos")
    fig4 = px.scatter(
        df_filtrado, 
        x='temperatura_c', 
        y='tasa_defectos_pct',
        color='linea_produccion',
        trendline='ols'
    )
    fig4.update_layout(height=350, xaxis_title="Temperatura (°C)", yaxis_title="Tasa Defectos (%)")
    st.plotly_chart(fig4, width='stretch')

st.markdown("---")

# ─── SECCIÓN 4: EVOLUCIÓN TEMPORAL ───────────────────────────────
st.subheader("📈 Evolución de Producción Semanal")
prod_sem = df_filtrado.groupby('semana', as_index=False)['unidades_producidas'].sum().sort_values('semana')

fig5 = px.line(
    prod_sem, 
    x='semana', 
    y='unidades_producidas', 
    markers=True
)
fig5.update_traces(line_color='#2563eb', line_width=3, marker=dict(size=8, color='#1e40af'))
fig5.update_layout(height=350, xaxis_title="Semana", yaxis_title="Unidades Producidas", xaxis=dict(dtick=4))
st.plotly_chart(fig5, width='stretch')
