import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import urllib.parse
import os

# Configuración inicial de la página
st.set_page_config(page_title="Caja Taller Automotriz César Beto", page_icon="🚗", layout="centered")

RUTA_ARCHIVO = "taller_datos.xlsx"

# --- GENERAR DATOS DE PRUEBA PARA UN MES COMPLETO ---
def generar_datos_mes_completo():
    datos = []
    hoy = datetime.now()
    
    marcas = ["Toyota", "Hyundai", "Nissan", "Chevrolet", "Kia", "Suzuki", "Mazda", "Volkswagen", "Renault"]
    trabajos = [
        "Pintado Parachoques Delantero", "Pintado Parachoques Trasero", 
        "Pintado de Puerta Delantera", "Pintado Guardafango", 
        "Pintura Completa Auto", "Pulido y Lijado General", "Adelanto / Cuenta de Trabajo"
    ]
    materiales = ["Lijas de agua", "Pintura Poliuretano", "Laca Transparente", "Catalizador", "Masilla plástica", "Cinta masking tape"]
    personales = ["Almuerzo", "Desayuno", "Agua / Gaseosa", "Pasajes / Movilidad", "Recarga de celular"]

    # Generar registros de los últimos 30 días
    for i in range(30):
        dia_pasado = hoy - timedelta(days=i)
        fecha_str = dia_pasado.strftime("%d/%m/%Y")
        mes_anio_str = dia_pasado.strftime("%m/%Y")
        
        # Simular ingresos por autos (algunos días sí, otros no)
        if i % 2 == 0:
            marca = marcas[i % len(marcas)]
            trabajo = trabajos[i % len(trabajos)]
            monto_auto = float(120 + (i * 15) % 300)
            medio = "📱 Digital (Yape / Banco)" if i % 3 == 0 else "💵 Efectivo"
            datos.append({
                "fecha": fecha_str,
                "mes_anio": mes_anio_str,
                "tipo": "🚙 Orden de Trabajo / Cobro por Auto (Ingreso)",
                "detalle": f"Auto: {marca} | Placa/Ref: ABC-{100+i} | Trabajo: {trabajo}",
                "medio": medio,
                "monto": monto_auto
            })
            
        # Simular gastos de taller
        if i % 3 == 0:
            material = materiales[i % len(materiales)]
            datos.append({
                "fecha": fecha_str,
                "mes_anio": mes_anio_str,
                "tipo": "🔴 Gastos Materiales y Herramientas (Taller)",
                "detalle": material,
                "medio": "💵 Efectivo",
                "monto": float(30 + (i * 5) % 70)
            })
            
        # Simular gastos personales diarios
        gasto_per = personales[i % len(personales)]
        datos.append({
            "fecha": fecha_str,
            "mes_anio": mes_anio_str,
            "tipo": "🟡 Gastos Personales",
            "detalle": gasto_per,
            "medio": "💵 Efectivo",
            "monto": float(15 + (i * 2) % 25)
        })
        
    return datos

# --- FUNCIONES DE CARGA Y GUARDADO EN EXCEL ---
def cargar_datos_excel():
    if os.path.exists(RUTA_ARCHIVO):
        try:
            df_existente = pd.read_excel(RUTA_ARCHIVO)
            if df_existente.empty:
                return generar_datos_mes_completo()
            operaciones = []
            for _, row in df_existente.iterrows():
                operaciones.append({
                    "fecha": str(row.get("Fecha", "")),
                    "mes_anio": str(row.get("MesAnio", "")),
                    "tipo": str(row.get("Tipo", "")),
                    "detalle": str(row.get("Detalle", "")),
                    "medio": str(row.get("Medio", "")),
                    "monto": float(row.get("Monto", 0.0))
                })
            return operaciones
        except Exception:
            return generar_datos_mes_completo()
    else:
        datos_iniciales = generar_datos_mes_completo()
        guardar_datos_excel(datos_iniciales)
        return datos_iniciales

def guardar_datos_excel(lista_operaciones):
    try:
        df = pd.DataFrame(lista_operaciones)
        df.columns = ["Fecha", "MesAnio", "Tipo", "Detalle", "Medio", "Monto"]
        df.to_excel(RUTA_ARCHIVO, index=False)
    except Exception as e:
        st.error(f"Error al guardar en el archivo de Excel: {e}")

# Estilos CSS
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
    .card-orden { background-color: #f0fdf4; padding: 12px 16px; border-radius: 10px; border-left: 5px solid #22c55e; margin-bottom: 10px; color: #166534; }
    .card-taller { background-color: #fee2e2; padding: 10px 14px; border-radius: 10px; border-left: 5px solid #ef4444; margin-bottom: 8px; color: #991b1b; }
    .card-personal { background-color: #fef3c7; padding: 10px 14px; border-radius: 10px; border-left: 5px solid #f59e0b; margin-bottom: 8px; color: #92400e; }
    .metric-container { background-color: #f8fafc; border: 1px solid #e2e8f0; padding: 15px; border-radius: 12px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 15px; }
    .cierre-box { background-color: #f1f5f9; border: 2px dashed #0284c7; padding: 20px; border-radius: 12px; margin-top: 20px; }
    .admin-box { background-color: #fff1f2; border: 2px dashed #f43f5e; padding: 20px; border-radius: 12px; margin-top: 20px; }
    .btn-whatsapp { display: block; background-color: #25d366; color: white; padding: 12px 20px; border-radius: 10px; text-decoration: none; font-weight: bold; text-align: center; width: 100%; margin-top: 15px; font-size: 1rem; }
    .btn-whatsapp:hover { background-color: #22bf5b; color: white; }
    </style>
""", unsafe_allow_html=True)

# Inicializar Base de Datos en sesión cargando desde Excel
if 'operaciones' not in st.session_state:
    st.session_state.operaciones = cargar_datos_excel()

if 'efectivo_base' not in st.session_state:
    st.session_state.efectivo_base = 350.0

if 'digital_base' not in st.session_state:
    st.session_state.digital_base = 500.0

# Banner visual de pintura automotriz
st.markdown("""
    <div class="banner-taller">
        <h1 style="margin:0; font-size: 2rem; color: #ffffff; text-shadow: 2px 2px 4px rgba(0,0,0,0.7);">🚗 Taller de Pintura Automotriz César Beto</h1>
        <p style="margin:5px 0 0 0; color: #e2e8f0; font-size: 1.1rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.7);">Historial Completo de 30 Días en la Nube / Local</p>
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

# Selector principal de qué tipo de registro vas a hacer
tipo = st.selectbox("Seleccione qué desea registrar:", [
    "🚙 Orden de Trabajo / Cobro por Auto (Ingreso)", 
    "🔴 Gastos Materiales y Herramientas (Taller)", 
    "🟡 Gastos Personales"
], key="select_tipo_op_principal")

st.write("")

# --- FORMULARIO DE REGISTRO RÁPIDO ---
with st.form("form_registro", clear_on_submit=True):
    detalle = ""
    
    if "Orden de Trabajo" in tipo:
        st.markdown("### 🚙 Detalle de la Orden del Vehículo")
        marcas = [
            "Toyota", "Hyundai", "Nissan", "Chevrolet", "Kia", "Suzuki", 
            "Mazda", "Volkswagen", "Renault", "Chery", "Subaru", "Mitsubishi", "Honda", "Otro"
        ]
        trabajos = [
            "Pintado Parachoques Delantero", "Pintado Parachoques Trasero", 
            "Pintado de Puerta Delantera", "Pintado de Puerta Trasera", 
            "Pintado Guardafango", "Pintado Capot", "Pintado Tapa / Baúl", 
            "Pintado Techo", "Pintura Completa Auto", "Pulido y Lijado General", 
            "Pulido de Faros", "Enderezado y Pintura Completa", "Adelanto / Cuenta de Trabajo"
        ]
        
        col_m, col_placa = st.columns(2)
        with col_m:
            m_elegida = st.selectbox("Marca del Auto:", marcas)
        with col_placa:
            placa_auto = st.text_input("Placa / N° de Orden (Ej: ABC-123 o Boleta 001):")
            
        t_elegido = st.selectbox("Trabajos realizados en este vehículo:", trabajos)
        observaciones_auto = st.text_input("Notas (Ej: Incluye material, pintura y mano de obra):")
        
        detalle = f"Auto: {m_elegida} | Placa/Ref: {placa_auto if placa_auto else 'S/N'} | Trabajo: {t_elegido}"
        if observaciones_auto:
            detalle += f" | Nota: {observaciones_auto}"

    elif "Gastos Materiales" in tipo:
        st.markdown("### 🔴 Gasto de Insumos / Taller")
        materiales = [
            "Lijas de agua (Grano fino/medio)", "Lijas secas / lija de fierro", 
            "Pintura Poliuretano / Base color", "Laca Transparente / Clear", 
            "Catalizador / Endurecedor", "Tiner acrílico / de poliuretano", 
            "Masilla plástica / de polímero", "Primer / Base primer anticorrosivo",
            "Cinta masking tape (Azul / Papel)", "Papel craft / Plástico para enmascarar", 
            "Masilla rápida / Filler", "Discos de corte / Lija de copa",
            "Compra o reparación de Herramienta", "Pago de luz / agua del taller"
        ]
        mat_elegido = st.selectbox("Material / Herramienta:", materiales)
        desc_libre = st.text_input("Detalle extra (opcional):")
        detalle = mat_elegido
        if desc_libre:
            detalle += f" - {desc_libre}"

    else: 
        st.markdown("### 🟡 Gasto Personal")
        personales = [
            "Almuerzo", "Desayuno", "Cena", "Agua / Gaseosa / Refrigerio",
            "Bebidas / Cerveza", "Pasajes / Movilidad / Taxi", "Cochera / Estacionamiento",
            "Recarga de celular / Datos", "Farmacia / Medicamentos", "Ropa / Calzado", "Regalos / Varios"
        ]
        per_elegido = st.selectbox("Categoría Personal:", personales)
        desc_libre = st.text_input("Detalle extra (opcional):")
        detalle = per_elegido
        if desc_libre:
            detalle += f" - {desc_libre}"

    col_monto, col_medio = st.columns(2)
    with col_monto:
        monto = st.number_input("Monto Total ($ / S/):", min_value=0.0, step=1.0, format="%.2f")
    with col_medio:
        medio_pago = st.selectbox("Medio de Pago / Cobro:", ["💵 Efectivo", "📱 Digital (Yape / Banco)"])
    
    enviado = st.form_submit_button("Guardar Registro")
    
    if enviado:
        if monto <= 0:
            st.error("Por favor ingresa un monto válido mayor a 0.")
        else:
            now = datetime.now()
            fecha_str = now.strftime("%d/%m/%Y")
            mes_anio_str = now.strftime("%m/%Y")
            
            nueva_op = {
                "fecha": fecha_str,
                "mes_anio": mes_anio_str,
                "tipo": tipo,
                "detalle": detalle,
                "medio": medio_pago,
                "monto": monto
            }
            
            st.session_state.operaciones.insert(0, nueva_op)
            guardar_datos_excel(st.session_state.operaciones)
            
            st.success("¡Guardado exitosamente en el archivo!")
            st.rerun()

# --- CÁLCULOS FINANCIEROS GLOBALES Y POR MEDIO ---
df = pd.DataFrame(st.session_state.operaciones)

total_ingresos = 0.0
total_gastos_taller = 0.0
total_gastos_personal = 0.0

efectivo_neto_movs = 0.0
digital_neto_movs = 0.0

if not df.empty:
    total_ingresos = df[df['tipo'].str.contains("Orden de Trabajo")]['monto'].sum()
    total_gastos_taller = df[df['tipo'].str.contains("Gastos Materiales")]['monto'].sum()
    total_gastos_personal = df[df['tipo'].str.contains("Gastos Personales")]['monto'].sum()

    for _, row in df.iterrows():
        es_ingreso = "Orden de Trabajo" in str(row['tipo'])
        valor = float(row['monto']) if es_ingreso else -float(row['monto'])
        
        if "Efectivo" in str(row['medio']):
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
    st.metric("🟢 Cobros de Órdenes (Autos)", f"${total_ingresos:.2f}")
    st.metric("🔴 Gasto Total Insumos Taller", f"${total_gastos_taller:.2f}")
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

    f_ingresos = df_filtrado[df_filtrado['tipo'].str.contains("Orden de Trabajo")]['monto'].sum() if not df_filtrado.empty else 0
    f_g_taller = df_filtrado[df_filtrado['tipo'].str.contains("Materiales")]['monto'].sum() if not df_filtrado.empty else 0
    f_g_personal = df_filtrado[df_filtrado['tipo'].str.contains("Gastos Personales")]['monto'].sum() if not df_filtrado.empty else 0
    f_ganancia_periodo = f_ingresos - (f_g_taller + f_g_personal)

    col1, col2, col3 = st.columns(3)
    col1.metric("Ingresos Periodo", f"${f_ingresos:.2f}")
    col2.metric("Gastos Periodo", f"${(f_g_taller + f_g_personal):.2f}")
    col3.metric("Ganancia Periodo", f"${f_ganancia_periodo:.2f}")

    st.write("---")

    # --- TARJETAS INDIVIDUALES ---
    for index, row in df_filtrado.iterrows():
        if "Orden de Trabajo" in str(row['tipo']):
            clase = "card-orden"
            signo = "+"
            cat = "🚗 Orden de Auto"
        elif "Materiales" in str(row['tipo']):
            clase = "card-taller"
            signo = "-"
            cat = "🔴 Insumo Taller"
        else:
            clase = "card-personal"
            signo = "-"
            cat = "🟡 Gasto Personal"

        medio_icono = "💵" if "Efectivo" in str(row['medio']) else "📱"

        st.markdown(f"""
            <div class="{clase}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>{row['detalle']}</strong><br>
                        <small><b>{cat}</b> ({medio_icono} {row['medio']}) | {row['fecha']}</small>
                    </div>
                    <div style="font-size: 1.1rem; font-weight: bold;">
                        {signo}${float(row['monto']):.2f}
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.write("---")
    st.subheader("🖨️ Tablas y Reportes Detallados")

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
    st.info("No hay registros todavía.")

# --- SECCIÓN DE ADMINISTRAR / CORREGIR REGISTROS ---
st.write("---")
st.markdown("""
    <div class="admin-box">
        <h3 style="margin-top:0; color: #e11d48;">⚙️ Administrar y Corregir Registros</h3>
        <p style="color: #334155; font-size: 0.95rem;">
            ¿Te equivocaste en un monto o descripción? Selecciona la operación que deseas eliminar de la lista.
        </p>
    </div>
""", unsafe_allow_html=True)

if not df.empty:
    opciones_borrar = []
    for idx, row in df.iterrows():
        etiqueta_corta = f"[{row['fecha']}] {row['detalle']} - ${float(row['monto']):.2f} ({row['medio']})"
        opciones_borrar.append((idx, etiqueta_corta))
    
    seleccion_a_borrar = st.selectbox(
        "Selecciona el registro incorrecto para eliminar:", 
        options=[item[0] for item in opciones_borrar],
        format_func=lambda x: next(item[1] for item in opciones_borrar if item[0] == x)
    )
    
    col_del1, col_del2 = st.columns([1, 2])
    with col_del1:
        if st.button("🗑️ Eliminar Registro", type="primary"):
            st.session_state.operaciones.pop(seleccion_a_borrar)
            guardar_datos_excel(st.session_state.operaciones)
            st.success("¡Registro eliminado correctamente!")
            st.rerun()
else:
    st.info("No hay registros para corregir o eliminar todavía.")

# --- SECCIÓN DE CIERRE DE CAJA DIARIO Y WHATSAPP ---
st.write("---")
st.markdown("""
    <div class="cierre-box">
        <h3 style="margin-top:0; color: #0284c7;">🔒 Cierre de Caja y Envío a WhatsApp (984116361)</h3>
        <p style="color: #334155; font-size: 0.95rem;">
            Aquí puedes revisar el reporte resumido del día de hoy listo para enviarlo a tu WhatsApp personal con un solo clic.
        </p>
    </div>
""", unsafe_allow_html=True)

df_hoy_wa = df[df['fecha'] == fecha_hoy] if not df.empty else pd.DataFrame()

if not df_hoy_wa.empty:
    f_ing_hoy = df_hoy_wa[df_hoy_wa['tipo'].str.contains("Orden de Trabajo")]['monto'].sum()
    f_gt_hoy = df_hoy_wa[df_hoy_wa['tipo'].str.contains("Materiales")]['monto'].sum()
    f_gp_hoy = df_hoy_wa[df_hoy_wa['tipo'].str.contains("Gastos Personales")]['monto'].sum()
    f_gastos_hoy = f_gt_hoy + f_gp_hoy
    f_ganancia_hoy = f_ing_hoy - f_gastos_hoy
    
    msg = f"🔒 *CIERRE DE CAJA - TALLER CÉSAR BETO*\n"
    msg += f"📅 *Fecha:* {fecha_hoy}\n\n"
    msg += f"🟢 *Total Ingresos (Autos):* ${f_ing_hoy:.2f}\n"
    msg += f"🔴 *Total Gastos (Taller/Personal):* ${f_gastos_hoy:.2f}\n"
    msg += f"💰 *Ganancia Neta (Libre):* ${f_ganancia_hoy:.2f}\n\n"
    msg += f"💵 *Efectivo actual
