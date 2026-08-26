import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse

# Configuración inicial de la página
st.set_page_config(page_title="Caja Taller Automotriz", page_icon="🚗", layout="centered")

# Estilos CSS (Fondo claro, banner automotriz y tarjetas estilizadas)
st.markdown("""
    <style>
    .banner-taller {
        background: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), url('https://images.unsplash.com/photo-1563720223185-11003d516935?auto=format&fit=crop&w=1000&q=80');
        background-size: cover;
        background-position: center;
        padding: 30px;
        border-radius: 12px;
        text-align: center;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .card-ingreso { background-color: #dcfce7; padding: 10px 14px; border-radius: 10px; border-left: 5px solid #22c55e; margin-bottom: 8px; color: #166534; }
    .card-taller { background-color: #fee2e2; padding: 10px 14px; border-radius: 10px; border-left: 5px solid #ef4444; margin-bottom: 8px; color: #991b1b; }
    .card-personal { background-color: #fef3c7; padding: 10px 14px; border-radius: 10px; border-left: 5px solid #f59e0b; margin-bottom: 8px; color: #92400e; }
    .metric-container { background-color: #f8fafc; border: 1px solid #e2e8f0; padding: 15px; border-radius: 12px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 15px; }
    .btn-whatsapp { display: block; background-color: #25d366; color: white; padding: 12px 20px; border-radius: 10px; text-decoration: none; font-weight: bold; text-align: center; width: 100%; margin-top: 15px; font-size: 1rem; }
    .btn-whatsapp:hover { background-color: #22bf5b; color: white; }
    </style>
""", unsafe_allow_html=True)

# Inicializar Base de Datos y Saldos en la sesión
if 'operaciones' not in st.session_state:
    st.session_state.operaciones = []

if 'efectivo_base' not in st.session_state:
    st.session_state.efectivo_base = 0.0

if 'digital_base' not in st.session_state:
    st.session_state.digital_base = 0.0

# Banner visual de pintura automotriz
st.markdown("""
    <div class="banner-taller">
        <h1 style="margin:0; font-size: 2rem; color: #ffffff; text-shadow: 2px 2px 4px rgba(0,0,0,0.7);">🚗 Taller de Pintura Automotriz César Beto</h1>
        <p style="margin:5px 0 0 0; color: #e2e8f0; font-size: 1.1rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.7);">Control de Caja, Efectivo y Digital</p>
    </div>
""", unsafe_allow_html=True)

# --- CONFIGURACIÓN DE DINERO INICIAL ---
with st.expander("⚙️ Configurar Dinero Inicial (Efectivo y Digital)"):
    col_eb, col_db = st.columns(2)
    with col_eb:
        nuevo_efectivo = st.number_input("Base en Efectivo ($ / S/):", value=st.session_state.efectivo_base, step=10.0)
    with col_db:
        nuevo_digital = st.number_input("Base Digital / Yape ($ / S/):", value=st.session_state.digital_base, step=10.0)
        
    if st.button("Fijar Saldos Base"):
        st.session_state.efectivo_base = nuevo_efectivo
        st.session_state.digital_base = nuevo_digital
        st.success("¡Saldos iniciales actualizados correctamente!")

# Selector principal de categoría fuera del formulario (cambio ultra rápido sin congelarse)
tipo = st.selectbox("Tipo de Operación:", [
    "🟢 Ingresos de Pintura / Taller", 
    "🔴 Gastos Materiales y Herramientas", 
    "🟡 Gastos Personales"
], key="select_tipo_op_principal")

st.write("")

# --- FORMULARIO DE REGISTRO RÁPIDO ---
with st.form("form_registro", clear_on_submit=True):
    detalle = ""
    
    # 1. Si es Ingreso (Ampliando marcas y trabajos detallados)
    if "Ingresos" in tipo:
        marcas = [
            "Toyota", "Hyundai", "Nissan", "Chevrolet", "Kia", "Suzuki", 
            "Mazda", "Volkswagen", "Renault", "Chery", "Subaru", "Mitsubishi", "Honda", "Otro"
        ]
        trabajos = [
            "Pintado Parachoques Delantero", 
            "Pintado Parachoques Trasero", 
            "Pintado de Puerta Delantera", 
            "Pintado de Puerta Trasera", 
            "Pintado Guardafango", 
            "Pintado Capot", 
            "Pintado Tapa / Baúl", 
            "Pintado Techo", 
            "Pintura Completa Auto", 
            "Pulido y Lijado General", 
            "Pulido de Faros",
            "Enderezado y Pintura",
            "Adelanto de Trabajo"
        ]
        
        col_m, col_t = st.columns(2)
        with col_m:
            m_elegida = st.selectbox("Marca del Auto:", marcas)
        with col_t:
            t_elegido = st.selectbox("Trabajo Realizado:", trabajos)
            
        desc_libre = st.text_input("Detalle extra (Ej: Color rojo perlado, placa...):")
        detalle = f"{t_elegido} ({m_elegida})"
        if desc_libre:
            detalle += f" - {desc_libre}"

    # 2. Si es Gasto de Taller (Ampliando materiales e insumos de pintura)
    elif "Gastos Materiales" in tipo:
        materiales = [
            "Lijas de agua (Grano fino/medio)", 
            "Lijas secas / lija de fierro", 
            "Pintura Poliuretano / Base color", 
            "Laca Transparente / Clear", 
            "Catalizador / Endurecedor",
            "Tiner acrílico / de poliuretano", 
            "Masilla plástica / de polímero", 
            "Primer / Base primer anticorrosivo",
            "Cinta masking tape (Azul / Papel)", 
            "Papel craft / Plástico para enmascarar", 
            "Masilla rápida / Filler",
            "Discos de corte / Lija de copa",
            "Compra o reparación de Herramienta",
            "Pago de luz / agua del taller"
        ]
        mat_elegido = st.selectbox("Material / Herramienta:", materiales)
        desc_libre = st.text_input("Detalle extra (opcional):")
        detalle = mat_elegido
        if desc_libre:
            detalle += f" - {desc_libre}"

    # 3. Si es Gasto Personal (Ampliando opciones del día a dia)
    else: 
        personales = [
            "Almuerzo", 
            "Desayuno", 
            "Cena", 
            "Agua / Gaseosa / Refrigerio",
            "Bebidas / Cerveza", 
            "Pasajes / Movilidad / Taxi", 
            "Cochera / Estacionamiento",
            "Recarga de celular / Datos",
            "Farmacia / Medicamentos",
            "Ropa / Calzado", 
            "Regalos / Varios"
        ]
        per_elegido = st.selectbox("Categoría Personal:", personales)
        desc_libre = st.text_input("Detalle extra (opcional):")
        detalle = per_elegido
        if desc_libre:
            detalle += f" - {desc_libre}"

    col_monto, col_medio = st.columns(2)
    with col_monto:
        monto = st.number_input("Monto ($ / S/):", min_value=0.0, step=1.0, format="%.2f")
    with col_medio:
        medio_pago = st.selectbox("Medio de Pago / Cobro:", ["💵 Efectivo", "📱 Digital (Yape / Banco)"])
    
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
                "medio": medio_pago,
                "fecha": now.strftime("%d/%m/%Y"),
                "mes_anio": now.strftime("%m/%Y")
            }
            st.session_state.operaciones.insert(0, nueva_op)
            st.success("¡Guardado con éxito!")
            st.rerun()

# --- CÁLCULOS FINANCIEROS GLOBALES Y POR MEDIO ---
df = pd.DataFrame(st.session_state.operaciones)

total_ingresos = 0.0
total_gastos_taller = 0.0
total_gastos_personal = 0.0

efectivo_neto_movs = 0.0
digital_neto_movs = 0.0

if not df.empty:
    total_ingresos = df[df['tipo'].str.contains("Ingresos")]['monto'].sum()
    total_gastos_taller = df[df['tipo'].str.contains("Materiales")]['monto'].sum()
    total_gastos_personal = df[df['tipo'].str.contains("Gastos Personales")]['monto'].sum()

    for _, row in df.iterrows():
        es_ingreso = "Ingresos" in row['tipo']
        valor = row['monto'] if es_ingreso else -row['monto']
        
        if "Efectivo" in row['medio']:
            efectivo_neto_movs += valor
        else:
            digital_neto_movs += valor

total_gastos_general = total_gastos_taller + total_gastos_personal
ganancia_neta = total_ingresos - total_gastos_general

efectivo_actual = st.session_state.efectivo_base + efectivo_neto_movs
digital_actual = st.session_state.digital_base + digital_neto_movs
saldo_total_libre = efectivo_actual + digital_actual

# --- PANEL DE ESTADÍSTICAS Y GANANCIAS ---
st.markdown("### 📈 Resumen Financiero Total")
col_g1, col_g2 = st.columns(2)
with col_g1:
    st.metric("🟢 Ingreso Total", f"${total_ingresos:.2f}")
    st.metric("🔴 Gasto Total Taller", f"${total_gastos_taller:.2f}")
with col_g2:
    st.metric("🟡 Gasto Total Personal", f"${total_gastos_personal:.2f}")
    st.metric("💰 Ganancia Neta Real", f"${ganancia_neta:.2f}")

# Panel de Dinero Disponible (Efectivo vs Digital)
st.markdown(f"""
    <div class="metric-container">
        <p style="margin:0; font-size: 0.9rem; color: #64748b; font-weight: bold;">DINERO DISPONIBLE TOTAL EN CAJA Y BANCO</p>
        <h1 style="margin:5px 0 5px 0; color: #0284c7;">${saldo_total_libre:.2f}</h1>
        <div style="display: flex; justify-content: space-around; margin-top: 10px; font-size: 0.95rem; border-top: 1px solid #e2e8f0; padding-top: 8px;">
            <span>💵 <b>Efectivo:</b> ${efectivo_actual:.2f}</span>
            <span>📱 <b>Digital / Yape:</b> ${digital_actual:.2f}</span>
        </div>
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
        st.subheader("📅 Resumen e Historial de Hoy")
    else:
        df_filtrado = df[df['mes_anio'] == mes_actual]
        st.subheader("📊 Resumen e Historial del Mes")

    f_ingresos = df_filtrado[df_filtrado['tipo'].str.contains("Ingresos")]['monto'].sum()
    f_gastos = df_filtrado[df_filtrado['tipo'].str.contains("Gastos|Materiales", regex=True)]['monto'].sum()

    col1, col2 = st.columns(2)
    col1.metric("Ingresos Periodo", f"${f_ingresos:.2f}")
    col2.metric("Gastos Periodo", f"${f_gastos:.2f}")

    st.write("---")

    # --- TARJETAS INDIVIDUALES ---
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

        medio_icono = "💵" if "Efectivo" in row['medio'] else "📱"

        st.markdown(f"""
            <div class="{clase}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>{row['detalle']}</strong><br>
                        <small><b>{cat}</b> ({medio_icono} {row['medio']}) | {row['fecha']}</small>
                    </div>
                    <div style="font-size: 1.1rem; font-weight: bold;">
                        {signo}${row['monto']:.2f}
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.write("---")
    st.subheader("🖨️ Cuadros y Reportes para Imprimir")
    st.write("Selecciona una opción para desplegar el cuadro completo en formato tabla listo para copiar o revisar:")

    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        ver_cuadro_dia = st.button("📋 Ver Cuadro del Día (Tabla)")
    with col_btn2:
        ver_cuadro_mes = st.button("📊 Ver Cuadro del Mes (Tabla)")

    if ver_cuadro_dia:
        st.markdown("### 📋 Cuadro Detallado del Día")
        df_hoy_tabla = df[df['fecha'] == fecha_hoy][['fecha', 'tipo', 'detalle', 'medio', 'monto']]
        if not df_hoy_tabla.empty:
            st.dataframe(df_hoy_tabla, use_container_width=True)
        else:
            st.info("No hay movimientos registrados para el día de hoy.")

    if ver_cuadro_mes:
        st.markdown("### 📊 Cuadro Detallado del Mes")
        df_mes_tabla = df[df['mes_anio'] == mes_actual][['fecha', 'tipo', 'detalle', 'medio', 'monto']]
        if not df_mes_tabla.empty:
            st.dataframe(df_mes_tabla, use_container_width=True)
        else:
            st.info("No hay movimientos registrados para este mes.")

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
    msg += f"💵 *Efectivo actual:* ${efectivo_actual:.2f}\n"
    msg += f"📱 *Digital actual:* ${digital_actual:.2f}\n"
    msg += f"💰 *Total en Caja/Banco:* ${saldo_total_libre:.2f}\n\n"
    msg += f"📋 *Detalle de operaciones:*\n"
    
    for index, row in df_hoy_wa.iterrows():
        signo = "+" if "Ingresos" in row['tipo'] else "-"
        medio_txt = "Efectivo" if "Efectivo" in row['medio'] else "Digital"
        msg += f"• {row['detalle']} ({medio_txt}): {signo}${row['monto']:.2f}\n"
    
    mensaje_codificado = urllib.parse.quote(msg)
    url_whatsapp = f"https://api.whatsapp.com/send?text={mensaje_codificado}"
    
    st.markdown(f'''
        <a href="{url_whatsapp}" target="_blank" class="btn-whatsapp">
            💬 Enviar Resumen de Hoy a WhatsApp
        </a>
    ''', unsafe_allow_html=True)
else:
    st.info("💡 Registra al menos un movimiento el día de hoy para habilitar el botón de envío automático a WhatsApp.")
