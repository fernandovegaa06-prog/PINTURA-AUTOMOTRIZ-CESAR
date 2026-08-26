import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse

# Configuración inicial de la página
st.set_page_config(page_title="Caja Taller Automotriz", page_icon="🚗", layout="centered")

# Estilos CSS con diseño automotriz (Fondo con tarjetas e imágenes de autos)
st.markdown("""
    <style>
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    .banner-taller {
        background: linear-gradient(rgba(15, 23, 42, 0.7), rgba(15, 23, 42, 0.7)), url('https://images.unsplash.com/photo-1486006920555-c77dce18193b?auto=format&fit=crop&w=1000&q=80');
        background-size: cover;
        background-position: center;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 20px;
        border: 1px solid #334155;
    }
    .card-ingreso { background-color: #064e3b; padding: 10px 14px; border-radius: 10px; border-left: 5px solid #22c55e; margin-bottom: 8px; color: #ecfdf5; }
    .card-taller { background-color: #7f1d1d; padding: 10px 14px; border-radius: 10px; border-left: 5px solid #ef4444; margin-bottom: 8px; color: #fef2f2; }
    .card-personal { background-color: #78350f; padding: 10px 14px; border-radius: 10px; border-left: 5px solid #f59e0b; margin-bottom: 8px; color: #fffbeb; }
    .metric-container { background-color: #1e293b; padding: 15px; border-radius: 15px; color: white; text-align: center; border: 1px solid #334155; }
    .btn-whatsapp { display: block; background-color: #25d366; color: white; padding: 12px 20px; border-radius: 10px; text-decoration: none; font-weight: bold; text-align: center; width: 100%; margin-top: 15px; font-size: 1rem; }
    .btn-whatsapp:hover { background-color: #22bf5b; color: white; }
    </style>
""", unsafe_allow_html=True)

# Inicializar Base de Datos en la sesión
if 'operaciones' not in st.session_state:
    st.session_state.operaciones = []

if 'saldo_base' not in st.session_state:
    st.session_state.saldo_base = 0.0

# Banner visual de carros / taller
st.markdown("""
    <div class="banner-taller">
        <h1 style="margin:0; font-size: 1.8rem; color: #38bdf8;">🚗 Taller Automotriz César Beto</h1>
        <p style="margin:5px 0 0 0; color: #cbd5e1;">Control Financiero Rápido y Profesional</p>
    </div>
""", unsafe_allow_html=True)

# --- CONFIGURACIÓN DE SALDO INICIAL ---
with st.expander("⚙️ Configurar Dinero Inicial / Base"):
    nuevo_saldo = st.number_input("Saldo base actual en Yape o Caja ($):", value=st.session_state.saldo_base, step=10.0)
    if st.button("Fijar Saldo Base"):
        st.session_state.saldo_base = nuevo_saldo
        st.success("¡Saldo base actualizado!")

# --- FUNCIÓN DE CAMBIO INSTANTÁNEO (EVITA QUE SE QUEDE PEGADO) ---
def actualizar_tipo():
    # Esta función limpia al instante cualquier retraso al cambiar de opción
    pass

# Selector principal fuera de formulario para respuesta inmediata
tipo = st.selectbox("Tipo de Operación:", [
    "🟢 Ingresos de Pintura / Taller", 
    "🔴 Gastos Materiales y Herramientas", 
    "🟡 Gastos Personales"
], on_change=actualizar_tipo, key="select_tipo_op_principal")

st.write("")

# --- FORMULARIO DE REGISTRO RÁPIDO ---
with st.form("form_registro", clear_on_submit=True):
    detalle = ""
    
    # 1. Si es Ingreso
    if "Ingresos" in tipo:
        marcas = ["Toyota", "Hyundai", "Nissan", "Chevrolet", "Kia", "Suzuki", "Mazda", "Volkswagen", "Otro"]
        trabajos = ["Pintado Parachoques Delantero", "Pintado Parachoques Trasero", "Pintado de Puerta", "Pintado Capot / Tapa", "Pintura Completa Auto", "Adelanto de Trabajo"]
        
        col_m, col_t = st.columns(2)
        with col_m:
            m_elegida = st.selectbox("Marca del Auto:", marcas)
        with col_t:
            t_elegido = st.selectbox("Trabajo Realizado:", trabajos)
            
        desc_libre = st.text_input("Detalle extra (opcional):")
        detalle = f"{t_elegido} ({m_elegida})"
        if desc_libre:
            detalle += f" - {desc_libre}"

    # 2. Si es Gasto de Taller
    elif "Gastos Materiales" in tipo:
        materiales = ["Lijas de agua / seca", "Pintura Poliuretano / Base", "Tiner / Disolvente", "Masilla plástica", "Cinta masking tape / Papel", "Compra de Herramienta"]
        mat_elegido = st.selectbox("Material / Herramienta:", materiales)
        desc_libre = st.text_input("Detalle extra (opcional):")
        detalle = mat_elegido
        if desc_libre:
            detalle += f" - {desc_libre}"

    # 3. Si es Gasto Personal
    else: 
        personales = [
            "Almuerzo", 
            "Desayuno", 
            "Cena", 
            "Bebidas / Cerveza", 
            "Ropa", 
            "Regalos", 
            "Pasajes / Movilidad"
        ]
        per_elegido = st.selectbox("Categoría Personal:", personales)
        desc_libre = st.text_input("Detalle extra (opcional):")
        detalle = per_elegido
        if desc_libre:
            detalle += f" - {desc_libre}"

    monto = st.number_input("Monto ($):", min_value=0.0, step=1.0, format="%.2f")
    
    enviado = st.form_submit_button("Guardar Operación")
    
    if enviado:
        if monto <= 0:
            st.error("Por favor ingresa un monto válido mayor a 0.")
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
            st.success("¡Guardado con éxito!")
            st.rerun()

# --- PROCESAMIENTO GENERAL ---
df = pd.DataFrame(st.session_state.operaciones)

total_ing_g = 0.0
total_gt_g = 0.0
total_gp_g = 0.0

if not df.empty:
    total_ing_g = df[df['tipo'].str.contains("Ingresos")]['monto'].sum()
    total_gt_g = df[df['tipo'].str.contains("Materiales")]['monto'].sum()
    total_gp_g = df[df['tipo'].str.contains("Gastos Personales")]['monto'].sum()

saldo_libre = st.session_state.saldo_base + total_ing_g - total_gt_g - total_gp_g

# Panel de Saldo Total
st.markdown(f"""
    <div class="metric-container">
        <p style="margin:0; font-size: 0.9rem; color: #94a3b8;">DINERO LIBRE DISPONIBLE</p>
        <h1 style="margin:5px 0 0 0; color: #38bdf8;">${saldo_libre:.2f}</h1>
    </div>
""", unsafe_allow_html=True)

st.write("")

# --- SELECTOR DE VISTA (HOY / MES) ---
filtro_tiempo = st.radio("Seleccionar Vista:", ["📅 Ver Hoy", "📊 Ver Todo el Mes"], horizontal=True)

fecha_hoy = datetime.now().strftime("%d/%m/%Y")
mes_actual = datetime.now().strftime("%m/%Y")

if not df.empty:
    if "Hoy" in filtro_tiempo:
        df_filtrado = df[df['fecha'] == fecha_hoy]
        st.subheader("📅 Resumen y Historial de Hoy")
    else:
        df_filtrado = df[df['mes_anio'] == mes_actual]
        st.subheader("📊 Resumen e Historial del Mes")

    f_ingresos = df_filtrado[df_filtrado['tipo'].str.contains("Ingresos")]['monto'].sum()
    f_gastos = df_filtrado[df_filtrado['tipo'].str.contains("Gastos|Materiales", regex=True)]['monto'].sum()

    col1, col2 = st.columns(2)
    col1.metric("Ingresos Periodo", f"${f_ingresos:.2f}")
    col2.metric("Gastos Periodo", f"${f_gastos:.2f}")

    st.write("---")

    # --- TARJETAS INDIVIDUALES (CUADROS) ---
    for index, row in df_filtrado.iterrows():
        if "Ingresos" in row['tipo']:
            clase = "card-ingreso"
            signo = "+"
            cat = "Ingreso Taller"
        elif "Materiales" in row['tipo']:
            clase = "card-taller"
            signo = "-"
            cat = "Gasto Taller"
        else:
            clase = "card-personal"
            signo = "-"
            cat = "Gasto Personal"

        st.markdown(f"""
            <div class="{clase}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>{row['detalle']}</strong><br>
                        <small><b>{cat}</b> | {row['fecha']}</small>
                    </div>
                    <div style="font-size: 1.1rem; font-weight: bold;">
                        {signo}${row['monto']:.2f}
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.write("---")
    st.subheader("🖨️ Reportes y Cierre de Día")

    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("🖨️ Ver Cuadro del Día"):
            df_hoy_excel = df[df['fecha'] == fecha_hoy][['fecha', 'tipo', 'detalle', 'monto']]
            if not df_hoy_excel.empty:
                st.success("Reporte del Día en formato tabla:")
                st.dataframe(df_hoy_excel, use_container_width=True)
            else:
                st.info("No hay movimientos registrados hoy.")

    with col_btn2:
        if st.button("🖨️ Ver Cuadro del Mes"):
            df_mes_excel = df[df['mes_anio'] == mes_actual][['fecha', 'tipo', 'detalle', 'monto']]
            if not df_mes_excel.empty:
                st.success("Reporte del Mes en formato tabla:")
                st.dataframe(df_mes_excel, use_container_width=True)
            else:
                st.info("No hay movimientos registrados este mes.")

else:
    st.info("No hay registros todavía. Empieza agregando tus operaciones arriba.")

# --- SECCIÓN DE WHATSAPP ---
st.write("---")
st.subheader("💬 Envío de Cierre a WhatsApp")

df_hoy_wa = df[df['fecha'] == fecha_hoy] if not df.empty else pd.DataFrame()

if not df_hoy_wa.empty:
    f_ing_hoy = df_hoy_wa[df_hoy_wa['tipo'].str.contains("Ingresos")]['monto'].sum()
    f_gas_hoy = df_hoy_wa[df_hoy_wa['tipo'].str.contains("Gastos|Materiales", regex=True)]['monto'].sum()
    
    msg = f"🚗 *REPORTE DIARIO - TALLER CÉSAR BETO*\n"
    msg += f"📅 *Fecha:* {fecha_hoy}\n\n"
    msg += f"🟢 *Ingresos del día:* ${f_ing_hoy:.2f}\n"
    msg += f"🔴 *Gastos del día:* ${f_gas_hoy:.2f}\n"
    msg += f"💵 *Dinero Libre Actual:* ${saldo_libre:.2f}\n\n"
    msg += f"📋 *Detalle de operaciones:*\n"
    
    for index, row in df_hoy_wa.iterrows():
        signo = "+" if "Ingresos" in row['tipo'] else "-"
        msg += f"• {row['detalle']}: {signo}${row['monto']:.2f}\n"
    
    mensaje_codificado = urllib.parse.quote(msg)
    url_whatsapp = f"https://api.whatsapp.com/send?text={mensaje_codificado}"
    
    st.markdown(f'''
        <a href="{url_whatsapp}" target="_blank" class="btn-whatsapp">
            💬 Enviar Resumen de Hoy a WhatsApp
        </a>
    ''', unsafe_allow_html=True)
else:
    st.info("💡 Registra al menos un ingreso o gasto el día de hoy para habilitar el botón de envío automático a WhatsApp.")
