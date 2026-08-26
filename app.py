import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración inicial de la página
st.set_page_config(page_title="Caja Taller Automotriz", page_icon="🚗", layout="centered")

# Estilos CSS personalizados para darle un look moderno de tarjetas (cuadros)
st.markdown("""
    <style>
    .card-ingreso { background-color: #dcfce7; padding: 12px; border-radius: 10px; border-left: 5px solid #22c55e; margin-bottom: 8px; color: #166534; }
    .card-taller { background-color: #fee2e2; padding: 12px; border-radius: 10px; border-left: 5px solid #ef4444; margin-bottom: 8px; color: #991b1b; }
    .card-personal { background-color: #fef3c7; padding: 12px; border-radius: 10px; border-left: 5px solid #f59e0b; margin-bottom: 8px; color: #92400e; }
    .metric-container { background-color: #1e293b; padding: 15px; border-radius: 15px; color: white; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# Inicializar Base de Datos en la sesión de Streamlit
if 'operaciones' not in st.session_state:
    st.session_state.operaciones = []

if 'saldo_base' not in st.session_state:
    st.session_state.saldo_base = 0.0

st.title("🚗 Control Financiero - César Beto")
st.write("Taller de Pintura Automotriz")

# --- CONFIGURACIÓN DE SALDO INICIAL ---
with st.expander("⚙️ Configurar Dinero Inicial / Base"):
    nuevo_saldo = st.number_input("Saldo base actual en Yape o Caja ($):", value=st.session_state.saldo_base, step=10.0)
    if st.button("Fijar Saldo Base"):
        st.session_state.saldo_base = nuevo_saldo
        st.success("¡Saldo base actualizado!")

# --- FORMULARIO DE REGISTRO ---
with st.form("form_registro", clear_on_submit=True):
    st.subheader("Registrar Movimiento")
    
    tipo = st.selectbox("Tipo de Operación:", [
        "🟢 Ingresos de Pintura / Taller", 
        "🔴 Gastos Materiales y Herramientas", 
        "🟡 Gastos Personales del Día"
    ])
    
    # Listas automáticas para el rubro automotriz
    detalle = ""
    if "Ingresos" in tipo:
        marcas = ["Toyota", "Hyundai", "Nissan", "Chevrolet", "Kia", "Suzuki", "Mazda", "Volkswagen"]
        trabajos = ["Pintado Parachoques Delantero", "Pintado Parachoques Trasero", "Pintado de Puerta", "Pintado Capot / Tapa", "Pintura Completa Auto", "Adelanto de Trabajo"]
        
        col_m, col_t = st.columns(2)
        with col_m:
            m_elegida = st.selectbox("Marca de Auto:", ["Seleccionar marca..."] + marcas)
        with col_t:
            t_elegido = st.selectbox("Trabajo Realizado:", ["Seleccionar trabajo..."] + trabajos)
            
        desc_personalizada = st.text_input("O escribe otro detalle personalizado:")
        
        # Armar descripción final
        partes = []
        if t_elegido != "Seleccionar trabajo...": partes.append(t_elegido)
        if m_elegida != "Seleccionar marca...": partes.append(f"({m_elegida})")
        if desc_personalizada: partes.append(desc_personalizada)
        detalle = " - ".join(partes)

    elif "Gastos Materiales" in tipo:
        materiales = ["Lijas de agua / seca", "Pintura Poliuretano / Base", "Tiner / Disolvente", "Masilla plástica", "Cinta masking tape / Papel", "Compra de Herramienta"]
        mat_elegido = st.selectbox("Material / Herramienta Rápida:", ["Seleccionar material..."] + materiales)
        desc_personalizada = st.text_input("O escribe otro detalle:")
        detalle = mat_elegido if mat_elegido != "Seleccionar material..." else desc_personalizada
        if mat_elegido != "Seleccionar material..." and desc_personalizada:
            detalle = f"{mat_elegido} - {desc_personalizada}"

    else: # Gasto Personal
        personales = ["Desayuno", "Almuerzo", "Cena", "Pasajes / Movilidad", "Una Chela / Ocio"]
        per_elegido = st.selectbox("Gasto Personal Rápido:", ["Seleccionar gasto..."] + personales)
        desc_personalizada = st.text_input("O escribe otro detalle personal:")
        detalle = per_elegido if per_elegido != "Seleccionar gasto..." else desc_personalizada
        if per_elegido != "Seleccionar gasto..." and desc_personalizada:
            detalle = f"{per_elegido} - {desc_personalizada}"

    monto = st.number_input("Monto ($):", min_value=0.0, step=1.0, format="%.2f")
    
    enviado = st.form_submit_button("Guardar Operación")
    
    if enviado:
        if not detalle or monto <= 0:
            st.error("Por favor completa el detalle y un monto válido mayor a 0.")
        else:
            now = datetime.now()
            nueva_op = {
                "tipo": tipo,
                "detalle": detalle,
                "monto": monto,
                "fecha": now.strftime("%d/%m/%Y"),
                "mes_anio": now.strftime("%m/%Y")
            }
            st.session_state.operaciones.insert(0, nueva_op)
            st.success("¡Guardado correctamente!")
            st.rerun()

# --- PROCESAMIENTO DE DATOS Y CALCULOS ---
df = pd.DataFrame(st.session_state.operaciones)

total_ingresos_global = 0.0
total_gasto_taller_global = 0.0
total_gasto_personal_global = 0.0

if not df.empty:
    total_ingresos_global = df[df['tipo'].str.contains("Ingresos")]['monto'].sum()
    total_gasto_taller_global = df[df['tipo'].str.contains("Materiales")]['monto'].sum()
    total_gasto_personal_global = df[df['tipo'].str.contains("Personales")]['monto'].sum()

saldo_actual_libre = st.session_state.saldo_base + total_ingresos_global - total_gasto_taller_global - total_gasto_personal_global

# Mostrar Saldo Libre Total
st.markdown(f"""
    <div class="metric-container">
        <p style="margin:0; font-size: 0.9rem; color: #94a3b8;">DINERO LIBRE DISPONIBLE</p>
        <h1 style="margin:5px 0 0 0; color: #38bdf8;">${saldo_actual_libre:.2f}</h1>
    </div>
""", unsafe_allow_html=True)

st.write("")

# --- FILTROS DE TIEMPO (HOY / MES) ---
filtro_tiempo = st.radio("Selecciona Vista:", ["📅 Ver Hoy", "📊 Ver Todo el Mes"], horizontal=True)

fecha_hoy_str = datetime.now().strftime("%d/%m/%Y")
mes_actual_str = datetime.now().strftime("%m/%Y")

if not df.empty:
    if "Hoy" in filtro_tiempo:
        df_filtrado = df[df['fecha'] == fecha_hoy_str]
        st.subheader("📅 Resumen de Hoy")
    else:
        df_filtrado = df[df['mes_anio'] == mes_actual_str]
        st.subheader("📊 Resumen del Mes Actual")

    # Métricas del filtro seleccionado
    f_ingresos = df_filtrado[df_filtrado['tipo'].str.contains("Ingresos")]['monto'].sum()
    f_gastos = df_filtrado[df_filtrado['tipo'].str.contains("Gastos")]['monto'].sum()

    col1, col2 = st.columns(2)
    col1.metric("Ingresos en este periodo", f"${f_ingresos:.2f}")
    col2.metric("Gastos en este periodo", f"${f_gastos:.2f}")

    st.write("---")
    st.subheader("Historial en Tarjetas (Cuadros)")

    for index, row in df_filtrado.iterrows():
        if "Ingresos" in row['tipo']:
            clase_css = "card-ingreso"
            signo = "+"
            cat_label = "Ingreso Taller"
        elif "Materiales" in row['tipo']:
            clase_css = "card-taller"
            signo = "-"
            cat_label = "Gasto Taller"
        else:
            clase_css = "card-personal"
            signo = "-"
            cat_label = "Gasto Personal"

        st.markdown(f"""
            <div class="{clase_css}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>{row['detalle']}</strong><br>
                        <small><b>{cat_label}</b> | Fecha: {row['fecha']}</small>
                    </div>
                    <div style="font-size: 1.1rem; font-weight: bold;">
                        {signo}${row['monto']:.2f}
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
else:
    st.info("Aún no hay movimientos registrados. ¡Empieza registrando arriba!")
