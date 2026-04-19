import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
import google.generativeai as genai

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="StatSoft · Análisis Estadístico",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── COQUETTE SOFT UI CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --rose:    #f2a7bb;
    --blush:   #f7d0dc;
    --lavender:#c9b8f5;
    --sky:     #b3d4f5;
    --cream:   #fdf8f2;
    --white:   #ffffff;
    --ink:     #4a3f5c;
    --muted:   #8c7fa0;
    --card:    rgba(255,255,255,0.72);
    --shadow:  0 8px 32px rgba(194,160,200,0.18);
    --glow:    0 0 0 2px rgba(201,184,245,0.35);
}

* { box-sizing: border-box; }

.stApp {
    background: linear-gradient(135deg, #fdf2f8 0%, #f0eaff 40%, #e8f3fc 100%);
    font-family: 'DM Sans', sans-serif;
    color: var(--ink);
}

/* ─ Sidebar ─ */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(255,255,255,0.9) 0%, rgba(240,234,255,0.85) 100%);
    border-right: 1px solid var(--blush);
    backdrop-filter: blur(12px);
}
section[data-testid="stSidebar"] .stRadio label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label {
    color: var(--ink) !important;
    font-size: 0.88rem;
}

/* ─ Headers ─ */
h1 { font-family: 'DM Serif Display', serif !important; color: var(--ink) !important; font-size: 2.4rem !important; }
h2, h3 { font-family: 'DM Serif Display', serif !important; color: var(--ink) !important; }
h4 { color: var(--muted) !important; font-weight: 500 !important; text-transform: uppercase; letter-spacing: 1.5px; font-size: 0.75rem !important; }

/* ─ Cards ─ */
.card {
    background: var(--card);
    border-radius: 22px;
    padding: 24px 26px;
    box-shadow: var(--shadow);
    border: 1px solid rgba(255,255,255,0.8);
    backdrop-filter: blur(8px);
    margin-bottom: 16px;
}

/* ─ Result badge ─ */
.result-badge {
    border-radius: 18px;
    padding: 20px 24px;
    border-left: 6px solid;
    box-shadow: var(--shadow);
    backdrop-filter: blur(8px);
}

/* ─ Buttons ─ */
.stButton > button {
    background: linear-gradient(135deg, var(--rose), var(--lavender));
    color: #fff;
    border: none;
    border-radius: 40px;
    padding: 10px 28px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    font-size: 0.9rem;
    letter-spacing: 0.4px;
    box-shadow: 0 4px 18px rgba(242,167,187,0.45);
    transition: all 0.25s ease;
    cursor: pointer;
}
.stButton > button:hover {
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 8px 24px rgba(201,184,245,0.5);
}
.stButton > button:active { transform: scale(0.98); }

/* ─ Inputs ─ */
input, .stSelectbox div[data-baseweb], .stNumberInput input, .stTextInput input {
    background: rgba(255,255,255,0.85) !important;
    border-radius: 12px !important;
    border: 1.5px solid var(--blush) !important;
    color: var(--ink) !important;
    font-family: 'DM Sans', sans-serif !important;
}
input:focus { box-shadow: var(--glow) !important; }

/* ─ Metrics ─ */
[data-testid="stMetricValue"] { color: var(--lavender) !important; font-family: 'DM Serif Display', serif !important; font-size: 1.6rem !important; }
[data-testid="stMetricLabel"] { color: var(--muted) !important; font-size: 0.78rem !important; text-transform: uppercase; letter-spacing: 1px; }

/* ─ Selectbox text ─ */
.stSelectbox label, .stSlider label, .stNumberInput label { color: var(--muted) !important; font-size: 0.82rem !important; font-weight: 500 !important; }

/* ─ Divider ─ */
hr { border-color: var(--blush) !important; opacity: 0.6; }

/* ─ Spinner / info ─ */
.stAlert { border-radius: 14px !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
        <div style='text-align:center; padding: 12px 0 6px;'>
            <span style='font-size:2rem;'>🎀</span>
            <h2 style='font-family:"DM Serif Display",serif; color:#4a3f5c; margin:6px 0 2px;'>StatSoft</h2>
            <p style='font-size:0.75rem; color:#8c7fa0; margin:0; letter-spacing:1.5px; text-transform:uppercase;'>Análisis estadístico</p>
        </div>
    """, unsafe_allow_html=True)
    st.divider()

    # API Key
    st.markdown("<h4>🔑 Google AI</h4>", unsafe_allow_html=True)
    api_key = st.text_input("API Key de Gemini", type="password", placeholder="Pega tu key aquí…")
    if api_key:
        genai.configure(api_key=api_key)
    st.divider()

    # Fuente de datos
    st.markdown("<h4>📂 Fuente de datos</h4>", unsafe_allow_html=True)
    metodo = st.radio("", ["Generación Sintética", "Carga de CSV"], label_visibility="collapsed")

    df = None
    if metodo == "Carga de CSV":
        archivo = st.file_uploader("Subir CSV", type=["csv"], label_visibility="collapsed")
        if archivo:
            df = pd.read_csv(archivo)
            st.success(f"✓ {archivo.name} cargado")
    else:
        distribucion = st.selectbox("Distribución base", ["Normal", "Sesgada (log-normal)", "Con outliers"])
        muestra = st.select_slider("Tamaño de muestra (n)", options=[50, 100, 250, 500, 1000], value=250)

        np.random.seed(42)
        if distribucion == "Normal":
            valores = np.random.normal(100, 15, muestra)
        elif distribucion == "Sesgada (log-normal)":
            valores = np.random.lognormal(mean=4.6, sigma=0.4, size=muestra)
        else:
            valores = np.concatenate([
                np.random.normal(100, 12, muestra - 15),
                np.random.normal(160, 5, 15)
            ])
        df = pd.DataFrame({'Valores': valores})

# ══════════════════════════════════════════════════════════════════════════════
# ENCABEZADO PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════
col_t1, col_t2 = st.columns([3, 1])
with col_t1:
    st.markdown("""
        <h1>Statistical Workspace <em style='color:#c9b8f5;font-style:italic;'>Pro</em></h1>
        <p style='color:#8c7fa0; font-size:0.95rem; margin-top:-8px;'>
            Visualización de distribuciones · Prueba Z · Asistente IA
        </p>
    """, unsafe_allow_html=True)
st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# CUERPO PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════
if df is not None:
    columna_activa = st.selectbox("Variable para análisis", df.columns)
    datos = df[columna_activa].dropna()
    n_obs      = len(datos)
    media_obs  = datos.mean()
    mediana_obs= datos.median()
    std_obs    = datos.std()
    skewness   = stats.skew(datos)
    kurt       = stats.kurtosis(datos)
    q1, q3     = datos.quantile(0.25), datos.quantile(0.75)
    iqr        = q3 - q1
    outliers   = datos[(datos < q1 - 1.5*iqr) | (datos > q3 + 1.5*iqr)]
    _, p_norm  = stats.shapiro(datos[:5000])   # Shapiro hasta 5 000

    # ── TABS ─────────────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["📊 Distribución", "🧪 Prueba Z", "🤖 Asistente IA"])

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1 — DISTRIBUCIÓN
    # ══════════════════════════════════════════════════════════════════════════
    with tab1:
        st.markdown("<h3 style='margin-bottom:4px;'>Exploración de la distribución</h3>", unsafe_allow_html=True)

        # Métricas rápidas
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("n", f"{n_obs:,}")
        m2.metric("Media", f"{media_obs:.2f}")
        m3.metric("Mediana", f"{mediana_obs:.2f}")
        m4.metric("Sesgo", f"{skewness:.3f}")
        m5.metric("Outliers", len(outliers))

        st.markdown("")
        col_hist, col_box = st.columns([3, 2], gap="medium")

        PALETTE = ["#f2a7bb", "#c9b8f5", "#b3d4f5", "#f7d0dc"]

        with col_hist:
            # Histograma + KDE
            fig_hist = go.Figure()
            fig_hist.add_trace(go.Histogram(
                x=datos, nbinsx=40, name="Frecuencia",
                marker_color="#c9b8f5", opacity=0.65,
                histnorm="probability density"
            ))
            # KDE
            kde_x = np.linspace(datos.min(), datos.max(), 300)
            kde_y = stats.gaussian_kde(datos)(kde_x)
            fig_hist.add_trace(go.Scatter(
                x=kde_x, y=kde_y, mode="lines", name="KDE",
                line=dict(color="#f2a7bb", width=2.5)
            ))
            fig_hist.update_layout(
                title="Histograma + KDE", template="simple_white",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", y=1.12),
                margin=dict(t=50, b=20, l=10, r=10), height=320,
                font=dict(family="DM Sans", color="#4a3f5c")
            )
            st.plotly_chart(fig_hist, use_container_width=True)

        with col_box:
            # Boxplot
            fig_box = go.Figure()
            fig_box.add_trace(go.Box(
                y=datos, name=columna_activa,
                marker_color="#f2a7bb",
                line_color="#c9b8f5",
                boxmean=True,
                fillcolor="rgba(201,184,245,0.25)"
            ))
            fig_box.update_layout(
                title="Boxplot", template="simple_white",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=50, b=20, l=10, r=10), height=320,
                showlegend=False,
                font=dict(family="DM Sans", color="#4a3f5c")
            )
            st.plotly_chart(fig_box, use_container_width=True)

        # ── Diagnóstico automático ────────────────────────────────────────
        normal_yn = "✅ Sí" if p_norm > 0.05 else "⚠️ No (Shapiro p < 0.05)"
        if abs(skewness) < 0.5:
            sesgo_txt = "✅ Sin sesgo relevante"
        elif skewness > 0:
            sesgo_txt = f"➡️ Sesgo positivo (cola derecha) — skew={skewness:.3f}"
        else:
            sesgo_txt = f"⬅️ Sesgo negativo (cola izquierda) — skew={skewness:.3f}"

        outlier_txt = (
            f"⚠️ {len(outliers)} outlier(s) detectado(s) (criterio IQR ×1.5)"
            if len(outliers) > 0 else "✅ Sin outliers detectados"
        )

        st.markdown(f"""
        <div class='card' style='margin-top:8px;'>
            <h4 style='margin-top:0;'>🔍 Diagnóstico automático</h4>
            <table style='width:100%; border-collapse:collapse; font-size:0.9rem; color:#4a3f5c;'>
                <tr>
                    <td style='padding:8px 12px; width:38%;'><b>¿Distribución normal?</b></td>
                    <td>{normal_yn}</td>
                </tr>
                <tr style='background:rgba(201,184,245,0.1);'>
                    <td style='padding:8px 12px;'><b>Sesgo</b></td>
                    <td>{sesgo_txt}</td>
                </tr>
                <tr>
                    <td style='padding:8px 12px;'><b>Outliers</b></td>
                    <td>{outlier_txt}</td>
                </tr>
                <tr style='background:rgba(201,184,245,0.1);'>
                    <td style='padding:8px 12px;'><b>Curtosis</b></td>
                    <td>{'Leptocúrtica (puntiaguda)' if kurt > 0.5 else 'Platicúrtica (achatada)' if kurt < -0.5 else 'Mesocúrtica (normal)'} — kurt={kurt:.3f}</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 2 — PRUEBA Z
    # ══════════════════════════════════════════════════════════════════════════
    with tab2:
        st.markdown("<h3 style='margin-bottom:4px;'>Prueba Z de una media</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color:#8c7fa0; font-size:0.85rem;'>Supuestos: varianza poblacional conocida · n ≥ 30</p>", unsafe_allow_html=True)

        col_params, col_viz = st.columns([1, 2], gap="large")

        with col_params:
            st.markdown("<div class='card'>", unsafe_allow_html=True)

            h0_valor    = st.number_input("H₀: media hipotética (μ₀)", value=round(float(media_obs), 2))
            sigma_pop   = st.number_input("Sigma poblacional (σ)", value=round(float(std_obs), 2), min_value=0.001)
            significancia = st.select_slider("Nivel de significancia (α)", options=[0.01, 0.05, 0.10], value=0.05)
            direccion   = st.selectbox("Tipo de prueba", ["Bilateral", "Cola izquierda", "Cola derecha"])

            # ── Hipótesis mostradas ──
            if direccion == "Bilateral":
                h1_texto = "H₁: μ ≠ μ₀"
            elif direccion == "Cola izquierda":
                h1_texto = "H₁: μ < μ₀"
            else:
                h1_texto = "H₁: μ > μ₀"

            st.markdown(f"""
            <div style='background:rgba(201,184,245,0.12); border-radius:12px; padding:12px 16px; margin:10px 0; font-size:0.88rem; color:#4a3f5c;'>
                <b>H₀</b>: μ = {h0_valor}<br>
                <b>{h1_texto}</b>
            </div>
            """, unsafe_allow_html=True)

            # ── Cálculos ──
            error_std   = sigma_pop / np.sqrt(n_obs) if n_obs > 0 else 1
            z_calc      = (media_obs - h0_valor) / error_std

            if direccion == "Bilateral":
                p_valor   = 2 * (1 - stats.norm.cdf(abs(z_calc)))
                z_critico = stats.norm.ppf(1 - significancia / 2)
                rechaza   = abs(z_calc) > z_critico
            elif direccion == "Cola izquierda":
                p_valor   = stats.norm.cdf(z_calc)
                z_critico = stats.norm.ppf(significancia)
                rechaza   = z_calc < z_critico
            else:
                p_valor   = 1 - stats.norm.cdf(z_calc)
                z_critico = stats.norm.ppf(1 - significancia)
                rechaza   = z_calc > z_critico

            color_res = "#f2a7bb" if rechaza else "#b3d4f5"
            emoji_res = "🎀" if rechaza else "🔵"
            txt_res   = "RECHAZAR H₀" if rechaza else "NO RECHAZAR H₀"

            st.markdown(f"""
            <div class='result-badge' style='background:rgba(255,255,255,0.75); border-left-color:{color_res}; margin-top:14px;'>
                <p style='margin:0; font-size:0.72rem; color:#8c7fa0; text-transform:uppercase; letter-spacing:1.5px;'>Decisión</p>
                <h2 style='color:{color_res}; margin:6px 0 10px; font-family:"DM Serif Display",serif;'>{emoji_res} {txt_res}</h2>
                <table style='font-size:0.88rem; color:#4a3f5c; border-collapse:collapse; width:100%;'>
                    <tr><td><b>Z calculado</b></td><td style='text-align:right;'>{z_calc:.4f}</td></tr>
                    <tr><td><b>Z crítico</b></td><td style='text-align:right;'>±{abs(z_critico):.4f}</td></tr>
                    <tr><td><b>p-value</b></td><td style='text-align:right;'>{p_valor:.5f}</td></tr>
                    <tr><td><b>Error estándar</b></td><td style='text-align:right;'>{error_std:.4f}</td></tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_viz:
            # ── Curva normal con región crítica ──
            x_range = np.linspace(-4, 4, 600)
            y_range = stats.norm.pdf(x_range)

            fig_z = go.Figure()

            # Región de NO rechazo
            fig_z.add_trace(go.Scatter(
                x=x_range, y=y_range,
                fill="tozeroy", fillcolor="rgba(179,212,245,0.25)",
                line=dict(color="rgba(0,0,0,0)"), name="No rechazo", showlegend=True
            ))

            # Regiones de rechazo
            def shade_rejection(x_arr, y_arr, label):
                fig_z.add_trace(go.Scatter(
                    x=x_arr, y=y_arr,
                    fill="tozeroy", fillcolor="rgba(242,167,187,0.45)",
                    line=dict(color="rgba(0,0,0,0)"), name=label, showlegend=True
                ))

            if direccion == "Bilateral":
                mask_l = x_range <= -abs(z_critico)
                mask_r = x_range >= abs(z_critico)
                shade_rejection(x_range[mask_l], y_range[mask_l], f"Rechazo α/2={significancia/2}")
                shade_rejection(x_range[mask_r], y_range[mask_r], f"Rechazo α/2={significancia/2}")
            elif direccion == "Cola izquierda":
                mask = x_range <= z_critico
                shade_rejection(x_range[mask], y_range[mask], f"Rechazo α={significancia}")
            else:
                mask = x_range >= z_critico
                shade_rejection(x_range[mask], y_range[mask], f"Rechazo α={significancia}")

            # Curva principal
            fig_z.add_trace(go.Scatter(
                x=x_range, y=y_range, mode="lines",
                line=dict(color="#c9b8f5", width=2.5), name="N(0,1)", showlegend=False
            ))

            # Z calculado (línea vertical)
            z_plot = max(-4, min(4, z_calc))
            fig_z.add_vline(
                x=z_plot, line_color="#f2a7bb" if rechaza else "#b3d4f5",
                line_width=2.5, line_dash="solid",
                annotation_text=f"Z={z_calc:.3f}",
                annotation_position="top right" if z_plot > 0 else "top left",
                annotation_font_color="#4a3f5c"
            )

            # Z crítico(s)
            if direccion == "Bilateral":
                for zc in [-abs(z_critico), abs(z_critico)]:
                    fig_z.add_vline(x=zc, line_color="#8c7fa0", line_width=1.5,
                                    line_dash="dash",
                                    annotation_text=f"±{abs(z_critico):.3f}",
                                    annotation_font_color="#8c7fa0")
            elif direccion == "Cola izquierda":
                fig_z.add_vline(x=z_critico, line_color="#8c7fa0", line_width=1.5,
                                line_dash="dash",
                                annotation_text=f"{z_critico:.3f}",
                                annotation_font_color="#8c7fa0")
            else:
                fig_z.add_vline(x=z_critico, line_color="#8c7fa0", line_width=1.5,
                                line_dash="dash",
                                annotation_text=f"{z_critico:.3f}",
                                annotation_font_color="#8c7fa0")

            fig_z.update_layout(
                title="Distribución N(0,1) · Región crítica y estadístico Z",
                template="simple_white",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", y=1.12, font=dict(size=11)),
                margin=dict(t=60, b=30, l=20, r=20), height=400,
                xaxis=dict(title="Z", range=[-4, 4], tickfont=dict(family="DM Sans")),
                yaxis=dict(title="f(z)", tickfont=dict(family="DM Sans")),
                font=dict(family="DM Sans", color="#4a3f5c")
            )
            st.plotly_chart(fig_z, use_container_width=True)

            # ── Interpretación automática ──
            interpretacion = (
                f"Con Z = {z_calc:.4f} y p = {p_valor:.5f} (α = {significancia}), "
                + ("se rechaza H₀. Hay evidencia estadística suficiente para afirmar que la media difiere de μ₀ = {:.2f}.".format(h0_valor)
                   if rechaza else
                   "no se rechaza H₀. No hay evidencia suficiente para concluir que la media difiere de μ₀ = {:.2f}.".format(h0_valor))
            )
            st.markdown(f"""
            <div class='card' style='margin-top:4px;'>
                <h4 style='margin-top:0;'>📝 Interpretación automática</h4>
                <p style='margin:0; font-size:0.9rem; color:#4a3f5c;'>{interpretacion}</p>
            </div>
            """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 3 — ASISTENTE IA
    # ══════════════════════════════════════════════════════════════════════════
    with tab3:
        st.markdown("<h3 style='margin-bottom:4px;'>🤖 Oráculo Estadístico</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color:#8c7fa0; font-size:0.85rem;'>Powered by Gemini 2.5 Flash</p>", unsafe_allow_html=True)

        # Construir variables localmente para que siempre existan en este tab
        _err = std_obs / np.sqrt(n_obs)
        _z   = (media_obs - float(df[columna_activa].dropna().mean())) / _err if _err != 0 else 0

        # Usar las variables de la prueba Z si ya se calcularon
        try:
            _z_calc   = z_calc
            _p_valor  = p_valor
            _rechaza  = rechaza
            _h0       = h0_valor
            _alpha    = significancia
            _dir      = direccion
            _sigma    = sigma_pop
        except NameError:
            _z_calc   = 0.0
            _p_valor  = 1.0
            _rechaza  = False
            _h0       = media_obs
            _alpha    = 0.05
            _dir      = "Bilateral"
            _sigma    = std_obs

        decision_usuario = st.radio(
            "¿Cuál es **tu** decisión estadística?",
            ["Rechazar H₀", "No rechazar H₀"],
            horizontal=True
        )

        prompt_extra = st.text_area(
            "¿Alguna pregunta o contexto adicional para la IA?",
            placeholder="p. ej. '¿Los supuestos de la prueba son razonables con estos datos?'",
            height=80
        )

        if st.button("✨ Generar análisis con IA"):
            if not api_key:
                st.warning("⚠️ Necesitas ingresar tu API Key de Google AI en el panel izquierdo.")
            else:
                decision_ia = "Rechazar H₀" if _rechaza else "No rechazar H₀"
                coincide    = decision_usuario == decision_ia

                prompt = f"""Eres un experto en estadística inferencial. Analiza los siguientes resultados de una prueba Z de una muestra:

**Resumen estadístico:**
- Media muestral: {media_obs:.4f}
- Mediana muestral: {mediana_obs:.4f}
- Desviación estándar muestral: {std_obs:.4f}
- Tamaño de muestra (n): {n_obs}
- Sesgo (skewness): {skewness:.4f}
- Curtosis: {kurt:.4f}
- Outliers detectados: {len(outliers)}

**Parámetros de la prueba:**
- H₀: μ = {_h0:.4f}
- Sigma poblacional (σ): {_sigma:.4f}
- Nivel de significancia (α): {_alpha}
- Tipo de prueba: {_dir}

**Resultados:**
- Estadístico Z calculado: {_z_calc:.4f}
- p-value: {_p_valor:.6f}
- Decisión automática: {"RECHAZAR H₀" if _rechaza else "NO RECHAZAR H₀"}
- Decisión del estudiante: {decision_usuario}
- ¿Coinciden? {"Sí ✅" if coincide else "No ❌"}

Responde en español. Estructura tu respuesta así:
1. Interpretación del estadístico Z y p-value.
2. ¿Es correcta la decisión del estudiante? Explica por qué.
3. ¿Los supuestos de la prueba Z son razonables aquí?
4. Una conclusión breve en lenguaje no técnico.

{f"Pregunta adicional del estudiante: {prompt_extra}" if prompt_extra.strip() else ""}
"""

                with st.spinner("🎀 Consultando al oráculo estadístico…"):
                    try:
                        model    = genai.GenerativeModel("gemini-2.5-flash")
                        respuesta = model.generate_content(prompt)

                        match_color = "#b3d4f5" if coincide else "#f2a7bb"
                        match_txt   = "✅ Tu decisión coincide con la decisión automática" if coincide else "❌ Tu decisión difiere de la decisión automática"

                        st.markdown(f"""
                        <div class='card' style='border-top: 4px solid {match_color};'>
                            <p style='margin:0; font-size:0.85rem; color:{match_color}; font-weight:600;'>{match_txt}</p>
                        </div>
                        """, unsafe_allow_html=True)

                        st.markdown(f"""
                        <div class='card'>
                            <h4 style='margin-top:0;'>🤖 Análisis de Gemini</h4>
                            <div style='font-size:0.9rem; color:#4a3f5c; line-height:1.7;'>
                                {respuesta.text.replace(chr(10), '<br>')}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    except Exception as e:
                        st.error(f"Error al conectar con Gemini: {e}")

else:
    st.markdown("""
    <div style='text-align:center; padding:80px 20px;'>
        <span style='font-size:3rem;'>🎀</span>
        <h2 style='color:#c9b8f5; font-family:"DM Serif Display",serif;'>Bienvenida al workspace</h2>
        <p style='color:#8c7fa0;'>Configura tu fuente de datos en el panel izquierdo para comenzar.</p>
    </div>
    """, unsafe_allow_html=True)
