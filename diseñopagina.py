import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
import google.generativeai as genai

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Statistical Analysis Pro - Soft UI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INYECCIÓN DE CSS AVANZADO (INSPIRADO EN LA IMAGEN) ---
# Este CSS crea las capas, sombras y colores de la UI inspirada.
st.markdown("""
    <style>
    /* Estilo general y fondo */
    .stApp {
        background-color: #f0f2f6; /* Gris muy suave de fondo */
        color: #555555;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }

    /* Títulos inspirados en el minimalismo */
    h1, h2, h3, h4 {
        color: #4a5568 !important;
        font-weight: 300 !important;
        letter-spacing: -0.5px;
    }
    
    /* Estilo de las "Cards" (las cajas blancas) */
    div[data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {
        background-color: #FFFFFF;
        padding: 25px;
        border-radius: 15px;
        border: 1px solid rgba(0, 0, 0, 0.03);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08); /* Sombra suave y profunda */
        margin-bottom: 20px;
    }

    /* Botones estilo "soft UI" azul */
    .stButton>button {
        background-color: #4da3ff; /* Azul suave y brillante */
        color: white;
        border: none;
        padding: 12px 28px;
        border-radius: 10px;
        font-weight: 600;
        box-shadow: 0 4px 10px rgba(77, 163, 255, 0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #3b8fd9;
        box-shadow: 0 6px 15px rgba(77, 163, 255, 0.5);
        color: white;
    }

    /* Inputs y Sidebar con estilo limpio */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stNumberInput>div>div>input {
        background-color: #f7f9fc !important;
        color: #4a5568 !important;
        border: 1px solid #e1e8f0 !important;
        border-radius: 8px !important;
    }
    
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #e1e8f0;
        box-shadow: 5px 0 15px rgba(0, 0, 0, 0.03);
    }
    
    /* Métricas con estilo de la imagen (pequeñas y claras) */
    [data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 300 !important;
        color: #4da3ff !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 1rem !important;
        font-weight: 400 !important;
        color: #a0aec0 !important;
    }

    /* División visual */
    .stDivider {
        border-color: #e1e8f0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

