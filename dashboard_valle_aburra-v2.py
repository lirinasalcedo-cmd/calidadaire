import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuración de página de Streamlit
st.set_page_config(
    page_title="Calidad del Aire y Salud - Valle de Aburrá",
    page_icon="🍃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS personalizado para mejorar la interfaz (colores modernos, tarjetas limpias)
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    h1, h2, h3 {
        color: #1e3d59;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 5px solid #17b978;
        margin-bottom: 20px;
    }
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        color: #17b978;
    }
    .metric-label {
        font-size: 14px;
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)

# Función para cargar datos de forma segura
@st.cache_data
def load_data():
    try:
        # Intentar cargar el dataset maestro de la ruta del proyecto
        df = pd.read_csv("dataset_maestro_sivigila_siata.csv")
    except FileNotFoundError:
        # Fallback si se ejecuta en otra carpeta local
        try:
            df = pd.read_csv("scratch/dataset_maestro_sivigila_siata.csv")
        except FileNotFoundError:
            st.error("No se encontró el archivo 'dataset_maestro_sivigila_siata.csv'. Asegúrate de que esté en la misma carpeta que este script.")
            return None
    
    df['fecha'] = pd.to_datetime(df['fecha'])
    return df

df = load_data()

if df is not None:
    # --- BARRA LATERAL (FILTROS) ---
    st.sidebar.image("https://img.icons8.com/illustrations/external-gradient-tal-revivo/100/external-meteorology-weather-forecast-with-air-pollutant-measure-clouds-gradient-tal-revivo.png", width=100)
    st.sidebar.title("Filtros del Panel")
    st.sidebar.markdown("Personaliza las visualizaciones del Valle de Aburrá:")
    
    # Filtro de Municipio (Medellín por defecto si existe)
    municipios = sorted(df['municipio'].unique())
    default_mun_idx = municipios.index('MEDELLIN') if 'MEDELLIN' in municipios else 0
    selected_mun = st.sidebar.selectbox("Selecciona un Municipio", municipios, index=default_mun_idx)
    
    # Filtro de Rango de Fechas
    min_date = df['fecha'].min().to_pydatetime()
    max_date = df['fecha'].max().to_pydatetime()
    selected_date_range = st.sidebar.date_input(
        "Rango de Fechas",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
    
    # Filtro de Contaminante Principal
    contaminantes = {
        'PM2.5 (Exposición Fina)': 'promedio_pm25',
        'Ozono (O3)': 'promedio_o3'
    }
    selected_poll_label = st.sidebar.selectbox("Contaminante de Enfoque", list(contaminantes.keys()))
    selected_poll_col = contaminantes[selected_poll_label]

    # Filtrar Dataset
    filtered_df = df[df['municipio'] == selected_mun].copy()
    if len(selected_date_range) == 2:
        start_date, end_date = pd.to_datetime(selected_date_range[0]), pd.to_datetime(selected_date_range[1])
        filtered_df = filtered_df[(filtered_df['fecha'] >= start_date) & (filtered_df['fecha'] <= end_date)]

    # --- ENCABEZADO ---
    st.title("🍃 Calidad del Aire y Enfermedades Respiratorias")
    st.subheader(f"Análisis de Correlación Histórica — Municipio: {selected_mun}")
    st.markdown("""
    Este dashboard dinámico e interactivo analiza la relación temporal entre las concentraciones de contaminantes atmosféricos (datos de **SIATA**) 
    y la incidencia de afecciones respiratorias graves y sistémicas pediátricas (datos de **SIVIGILA**).
    """)

    # --- TARJETAS DE MÉTRICAS (KPIs) ---
    col1, col2, col3, col4 = st.columns(4)
    
    avg_poll = filtered_df[selected_poll_col].mean()
    total_cases_sari = filtered_df['casos_sari_inusitada'].sum()
    total_cases_misc = filtered_df['casos_misc_pediatrico'].sum()
    total_cases = filtered_df['casos_totales_respiratorios'].sum()
    
    with col1:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #17b978;">
            <div class="metric-label">Promedio {selected_poll_label.split()[0]}</div>
            <div class="metric-value" style="color: #17b978;">{avg_poll:.2f} µg/m³</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #ff3f34;">
            <div class="metric-label">Casos Totales SIVIGILA</div>
            <div class="metric-value" style="color: #ff3f34;">{total_cases}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #ff9f1a;">
            <div class="metric-label">Casos SARI (IRAG)</div>
            <div class="metric-value" style="color: #ff9f1a;">{total_cases_sari}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #05c46b;">
            <div class="metric-label">Casos MIS-C (Pediatría)</div>
            <div class="metric-value" style="color: #05c46b;">{total_cases_misc}</div>
        </div>
        """, unsafe_allow_html=True)

    # --- PESTAÑAS DENTRO DEL PANEL ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Análisis de Series Temporales", 
        "🔗 Correlación de Retraso (Lags)", 
        "📊 Gráficos de Dispersión",
        "🗺️ Comparativa Municipal", 
        "📋 Explorar Dataset Maestro"
    ])

    # PESTAÑA 1: SERIES TEMPORALES
    with tab1:
        st.markdown("### Comportamiento en el Tiempo de la Contaminación vs. Casos de Salud")
        st.write("Explora gráficamente si los picos de contaminación preceden o coinciden con aumentos en las tasas de morbilidad respiratoria.")
        
        # Gráfico dinámico de doble eje con Plotly
        fig = make_subplots(specs=[[[{"secondary_y": True}]]])
        
        # Línea de contaminación (Media móvil 7 días)
        fig.add_trace(
            go.Scatter(
                x=filtered_df['fecha'], 
                y=filtered_df['pm25_media_movil_7d'] if selected_poll_col == 'promedio_pm25' else filtered_df[selected_poll_col], 
                name=f"{selected_poll_label} (Suavizado)",
                line=dict(color='#1e3d59', width=2),
                opacity=0.8
            ),
            secondary_y=False,
        )
        
        # Barras de casos totales de salud
        fig.add_trace(
            go.Bar(
                x=filtered_df['fecha'], 
                y=filtered_df['casos_totales_respiratorios'], 
                name="Casos de Salud Registrados",
                marker_color='#ff3f34',
                opacity=0.6
            ),
            secondary_y=True,
        )
        
        # Títulos y ejes
        fig.update_layout(
            title_text=f"Evolución Diaria en {selected_mun}",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            plot_bgcolor='white',
            margin=dict(l=20, r=20, t=50, b=20)
        )
        
        fig.update_xaxes(showgrid=True, gridcolor='#f1f1f1')
        fig.update_yaxes(title_text=f"Concentración de {selected_poll_label} (µg/m³)", secondary_y=False, showgrid=True, gridcolor='#f1f1f1')
        fig.update_yaxes(title_text="Número de Casos Reportados (SIVIGILA)", secondary_y=True)
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("💡 **Tip de Análisis:** Usa la barra de zoom en el gráfico para enfocarte en períodos específicos (como los meses de marzo o octubre, conocidos por transiciones climáticas en el Valle de Aburrá).")

    # PESTAÑA 2: CORRELACIÓN CON REZAGOS (LAGS)
    with tab2:
        st.markdown("### El Impacto del Retraso Temporal (Lags)")
        st.markdown("""
        Biológicamente, la exposición a altos niveles de material particulado o gases irritantes no siempre produce una hospitalización inmediata. 
        Suele existir un **rezago (lag)** de varios días mientras progresa la inflamación respiratoria. 
        Este análisis mide la correlación de Spearman para diferentes desfases en el tiempo:
        """)
        
        # Calcular coeficientes de Spearman dinámicos para lags del 0 al 7
        lags_range = range(0, 8)
        correlations = []
        
        # Para evitar mutar el dataframe original cached de streamlit, creamos una copia para el loop
        loop_df = filtered_df.copy()
        for lag in lags_range:
            if lag == 0:
                corr = loop_df[selected_poll_col].corr(loop_df['casos_totales_respiratorios'], method='spearman')
            else:
                loop_df[f'pollutant_lag_{lag}'] = loop_df[selected_poll_col].shift(lag)
                corr = loop_df[f'pollutant_lag_{lag}'].corr(loop_df['casos_totales_respiratorios'], method='spearman')
            correlations.append(corr if not pd.isna(corr) else 0.0)
            
        corr_df = pd.DataFrame({
            'Rezago Temporal': [f"Día {l} (Lag {l})" if l > 0 else "Mismo Día (Lag 0)" for l in lags_range],
            'Coeficiente de Correlación': correlations
        })
        
        # Graficar correlaciones
        fig_corr = px.bar(
            corr_df,
            x='Rezago Temporal',
            y='Coeficiente de Correlación',
            title=f"Fuerza de Relación entre Exposición a {selected_poll_label.split()[0]} y Admisión Respiratoria por Día de Rezago",
            labels={'Coeficiente de Correlación': 'Correlación de Spearman (r)'},
            color='Coeficiente de Correlación',
            color_continuous_scale=px.colors.sequential.Tealgrn,
            text_auto='.3f'
        )
        fig_corr.update_layout(plot_bgcolor='white', yaxis=dict(range=[0, max(correlations)*1.2 if max(correlations) > 0 else 0.5]))
        st.plotly_chart(fig_corr, use_container_width=True)
        
        # Interpretación médica
        max_idx = np.argmax(correlations)
        max_lag = lags_range[max_idx]
        max_corr = correlations[max_idx]
        
        st.success(f"""
        🔬 **Hallazgo Estadístico Clave en {selected_mun}:**  
        La correlación más fuerte ocurre con un rezago de **{max_lag} días (r = {max_corr:.3f})**.  
        Esto sugiere que un pico de contaminación por material particulado genera un incremento máximo de consultas médicas e ingresos hospitalarios aproximadamente **{max_lag} días después** del evento de contaminación ambiental.
        """)

    # PESTAÑA 3: GRÁFICOS DE DISPERSIÓN Y TENDENCIA MATEMÁTICA
    with tab3:
        st.markdown("### Gráficos de Dispersión y Modelado de Tendencia")
        st.markdown("""
        Un **gráfico de dispersión (Scatter Plot)** permite visualizar de forma directa la relación de causa y efecto. 
        Cada punto representa un día. En el eje horizontal (X) verás la contaminación, y en el vertical (Y) verás los casos de salud correspondientes.
        """)
        
        col_disp1, col_disp2 = st.columns([1, 3])
        
        with col_disp1:
            st.markdown("**Parámetros de Dispersión:**")
            selected_lag_scatter = st.slider(
                "Selecciona el Rezago (Lag) de contaminación",
                min_value=0,
                max_value=7,
                value=3,
                help="Grafica los casos de salud de un día contra la contaminación registrada X días atrás."
            )
            
            selected_y_scatter_label = st.selectbox(
                "Variable de Salud (Eje Y)",
                options=[
                    "Casos Totales Respiratorios",
                    "Casos SARI (IRAG Inusitada)",
                    "Tasas por 100,000 Habitantes"
                ]
            )
            
            y_scatter_map = {
                "Casos Totales Respiratorios": "casos_totales_respiratorios",
                "Casos SARI (IRAG Inusitada)": "casos_sari_inusitada",
                "Tasas por 100,000 Habitantes": "tasa_total_por_100k"
            }
            y_scatter_col = y_scatter_map[selected_y_scatter_label]
            
            # Preparar dataframe con el lag seleccionado
            scatter_df = filtered_df.copy()
            if selected_lag_scatter > 0:
                scatter_df['x_pollutant'] = scatter_df[selected_poll_col].shift(selected_lag_scatter)
                x_title = f"{selected_poll_label.split()[0]} con {selected_lag_scatter} días de Rezago (µg/m³)"
            else:
                scatter_df['x_pollutant'] = scatter_df[selected_poll_col]
                x_title = f"{selected_poll_label.split()[0]} del Mismo Día (µg/m³)"
                
            # Eliminar nulos generados por el shift
            scatter_df = scatter_df.dropna(subset=['x_pollutant', y_scatter_col])
            
            # Cálculo de correlación lineal para el texto
            pearson_r = scatter_df['x_pollutant'].corr(scatter_df[y_scatter_col], method='pearson')
            spearman_r = scatter_df['x_pollutant'].corr(scatter_df[y_scatter_col], method='spearman')
            
            st.metric("Correlación de Spearman (r)", f"{spearman_r:.3f}")
            st.metric("Correlación de Pearson (r)", f"{pearson_r:.3f}")
            st.caption("Un valor de *r* superior a 0.20 indica una asociación positiva relevante en estudios de epidemiología ambiental.")
            
        with col_disp2:
            # Gráfico de dispersión con línea de tendencia OLS
            fig_scatter = px.scatter(
                scatter_df,
                x='x_pollutant',
                y=y_scatter_col,
                trendline="ols",
                title=f"Dispersión de {selected_poll_label.split()[0]} vs. {selected_y_scatter_label} en {selected_mun}",
                labels={
                    'x_pollutant': x_title,
                    y_scatter_col: selected_y_scatter_label,
                    'categoria_ica_pm25': 'Categoría de Calidad del Aire'
                },
                color='categoria_ica_pm25',
                color_discrete_map={
                    "Buena": "#17b978",
                    "Regular / Aceptable": "#ff9f1a",
                    "Dañina para Grupos Sensibles": "#ff5e57",
                    "Dañina para la Salud": "#ff3f34",
                    "Muy Dañina / Alerta de Emergencia": "#8c1d40",
                    "Sin Datos": "#d2dae2"
                },
                hover_data=['fecha'],
                opacity=0.8
            )
            
            fig_scatter.update_layout(
                plot_bgcolor='white',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
                margin=dict(l=20, r=20, t=50, b=20)
            )
            fig_scatter.update_xaxes(showgrid=True, gridcolor='#f1f1f1')
            fig_scatter.update_yaxes(showgrid=True, gridcolor='#f1f1f1')
            
            st.plotly_chart(fig_scatter, use_container_width=True)
            
        st.info("""
        📈 **Cómo leer este gráfico:** La línea de tendencia inclinada hacia arriba demuestra visualmente la hipótesis científica del proyecto: 
        A medida que se incrementa la concentración de material contaminante en el aire (eje X), la probabilidad y frecuencia de hospitalizaciones 
        o casos de enfermedad respiratoria grave (eje Y) también aumenta de forma proporcional.
        """)

    # PESTAÑA 4: COMPARATIVA MUNICIPAL
    with tab4:
        st.markdown("### Comparación Territorial en el Valle de Aburrá")
        st.markdown("Compara las tasas de incidencia y los niveles de contaminación promedio entre los diferentes municipios del área metropolitana:")
        
        # Agrupar datos por municipio
        mun_compare = df.groupby('municipio').agg({
            'promedio_pm25': 'mean',
            'casos_totales_respiratorios': 'sum',
            'poblacion_estimada': 'first',
        }).reset_index()
        
        # Calcular tasa agregada por 100k
        mun_compare['tasa_incidencia_100k'] = (mun_compare['casos_totales_respiratorios'] / mun_compare['poblacion_estimada']) * 100000
        mun_compare = mun_compare.sort_values(by='promedio_pm25', ascending=False)
        
        col_m1, col_m2 = st.columns(2)
        
        with col_m1:
            fig_mun_poll = px.bar(
                mun_compare,
                x='municipio',
                y='promedio_pm25',
                title="Concentración Promedio Histórica de PM2.5 (µg/m³)",
                labels={'promedio_pm25': 'PM2.5 (µg/m³)', 'municipio': 'Municipio'},
                color='promedio_pm25',
                color_continuous_scale=px.colors.sequential.YlOrRd
            )
            fig_mun_poll.update_layout(plot_bgcolor='white')
            st.plotly_chart(fig_mun_poll, use_container_width=True)
            
        with col_m2:
            fig_mun_health = px.bar(
                mun_compare.sort_values(by='tasa_incidencia_100k', ascending=False),
                x='municipio',
                y='tasa_incidencia_100k',
                title="Tasa de Incidencia Acumulada de Salud (Casos por cada 100k hab.)",
                labels={'tasa_incidencia_100k': 'Casos/100k hab.', 'municipio': 'Municipio'},
                color='tasa_incidencia_100k',
                color_continuous_scale=px.colors.sequential.Purples
            )
            fig_mun_health.update_layout(plot_bgcolor='white')
            st.plotly_chart(fig_mun_health, use_container_width=True)

    # PESTAÑA 5: DATA EXPLORER
    with tab5:
        st.markdown("### Tabla Maestra de Datos Unificados")
        st.write("Usa esta pestaña para inspeccionar las filas integradas, realizar búsquedas rápidas o exportar el dataset como CSV para otros programas.")
        
        # Mostrar tabla interactiva con filtros
        st.dataframe(filtered_df[['fecha', 'municipio', 'promedio_pm25', 'promedio_o3', 'categoria_ica_pm25', 'casos_sari_inusitada', 'casos_misc_pediatrico', 'casos_totales_respiratorios', 'tasa_sari_por_100k']], use_container_width=True)
        
        # Descarga rápida de datos
        csv_data = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar datos filtrados como CSV",
            data=csv_data,
            file_name=f"calidad_aire_salud_{selected_mun}.csv",
            mime="text/csv",
        )
