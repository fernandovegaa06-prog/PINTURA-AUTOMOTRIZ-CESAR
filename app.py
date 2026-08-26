import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse
import os
import io

st.set_page_config(page_title="Caja Taller Automotriz César Beto", page_icon="🚗", layout="centered")

RUTA_ARCHIVO = "taller_datos.xlsx"

def cargar_datos_excel():
    if os.path.exists(RUTA_ARCHIVO):
        try:
            df_existente = pd.read_excel(RUTA_ARCHIVO, sheet_name="Operaciones")
            if df_existente.empty or 'Monto' not in df_existente.columns:
                return []
            operaciones = []
            for _, row in df_existente.iterrows():
                operaciones.append({
                    "fecha": str(row.get("Fecha", row.get("fecha", ""))),
                    "mes_anio": str(row.get("MesAnio", row.get("mes_anio", ""))),
                    "tipo": str(row.get("Tipo", row.get("tipo", ""))),
                    "detalle": str(row.get("Detalle", row.get("detalle", ""))),
                    "medio": str(row.get("Medio", row.get("medio", ""))),
                    "monto": float(row.get("Monto", row.get("monto", 0.0)))
                })
            return operaciones
        except Exception:
            return []
    else:
        return []

def guardar_datos_excel(lista_operaciones, total_ing, total_g_taller, total_g_pers, ganancia_neta, saldo_total):
    try:
        with pd.ExcelWriter(RUTA_ARCHIVO, engine='openpyxl') as writer:
            df_ops = pd.DataFrame(lista_operaciones)
            if not df_ops.empty:
                df_ops.columns = ["Fecha", "MesAnio", "Tipo", "Detalle", "Medio", "Monto"]
            else:
                df_ops = pd.DataFrame(columns=["Fecha", "MesAnio", "Tipo", "Detalle", "Medio", "Monto"])
            df_ops.to_excel(writer, sheet_name="Operaciones", index=False)
            
            df_resumen = pd.DataFrame({
                "Concepto": ["Total Ingresos", "Total Gastos Taller", "Total Gastos Personal", "Gasto Total General", "Ganancia Neta Real", "Dinero Disponible Total"],
                "Monto ($ / S/)": [total_ing, total_g_taller, total_g_pers, total_g_taller + total_g_pers, ganancia_neta, saldo_total]
            })
            df_resumen.to_excel(writer, sheet_name="Resumen_Financiero", index=False)
    except Exception:
        pass

st.markdown("""
    <style>
    .banner-taller { background: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), url('https://images.unsplash.com/photo-1563720223185-11003d516935?auto=format&fit=crop&w=1000&q=80'); background-size: cover; background-position: center; padding: 30px; border-radius: 12px; text-align: center; color: white; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
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

if 'operaciones' not in st.session_state:
    st.session_state.operaciones = cargar_datos_excel()

if 'efectivo_base' not in st.session_state:
    st.session_state.efectivo_base = 0.0

if 'digital_base' not in st.session_state:
    st.session_state.digital_base = 0.0

st.markdown("""
    <div class="banner-taller">
        <h1 style="margin:0; font-size: 2rem; color: #ffffff; text-shadow: 2px 2px 4px rgba(0,0,0,0.7);">🚗 Taller de Pintura Automotriz César Beto</h1>
        <p style="margin:5px 0 0 0; color: #e2e8f0; font-size: 1.1rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.7);">Control de Caja, Historial Diario y Reportes</p>
    </div>
""", unsafe_allow_html=True)

with st.expander("⚙️ Configurar Dinero Inicial en Caja"):
    col_eb, col_db = st.columns(2)
    with col_eb:
        nuevo_efectivo = st.number_input("Base en Efectivo ($ / S/):", value=st.session_state.efectivo_base, step=10.0)
    with col_db:
        nuevo_digital = st.number_input("Base Digital / Yape ($ / S/):", value=st.session_state.digital_base, step=10.0)
    if st.button("Fijar Saldos Base"):
        st.session_state.efectivo_base = nuevo_efectivo
        st.session_state.digital_base = nuevo_digital
        st.success("¡Saldos iniciales actualizados correctamente!")

tipo = st.selectbox("Seleccione qué desea registrar:", [
    "🚙 Orden de Trabajo / Cobro por Auto (Ingreso)", 
    "🔴 Gastos Materiales y Herramientas (Taller)", 
    "🟡 Gastos Personales"
], key="select_tipo_op_principal")

st.write("")

with st.form("form_registro", clear_on_submit=True):
    detalle = ""
    if "Orden de Trabajo" in tipo:
        st.markdown("### 🚙 Detalle de la Orden del Vehículo")
        marcas = ["Toyota", "Hyundai", "Nissan", "Chevrolet", "Kia", "Suzuki", "Mazda", "Volkswagen", "Renault", "Chery", "Subaru", "Mitsubishi", "Honda", "Otro"]
        trabajos = ["Pintado Parachoques Delantero", "Pintado Parachoques Trasero", "Pintado de Puerta Delantera", "Pintado de Puerta Trasera", "Pintado Guardafango", "Pintado Capot", "Pintado Tapa / Baúl", "Pintado Techo", "Pintura Completa Auto", "Pulido y Lijado General", "Pulido de Faros", "Enderezado y Pintura Completa", "Adelanto / Cuenta de Trabajo"]
        col_m, col_placa = st.columns(2)
        with col_m:
            m_elegida = st.selectbox("Marca del Auto:", marcas)
        with col_placa:
            placa_auto = st.text_input("Placa / N° de Orden:")
        t_elegido = st.selectbox("Trabajos realizados:", trabajos)
        observaciones_auto = st.text_input("Notas adicionales:")
        detalle = f"Auto: {m_elegida} | Placa/Ref: {placa_auto if placa_auto else 'S/N'} | Trabajo: {t_elegido}"
        if observaciones_auto:
            detalle += f" | Nota: {observaciones_auto}"
    elif "Gastos Materiales" in tipo:
        st.markdown("### 🔴 Gasto de Insumos / Taller")
        materiales = ["Lijas de agua", "Lijas secas", "Pintura Poliuretano", "Laca Transparente", "Catalizador", "Tiner acrílico", "Masilla plástica", "Primer", "Cinta masking tape", "Papel craft", "Masilla rápida", "Discos de corte", "Herramienta", "Pago de luz / agua"]
        mat_elegido = st.selectbox("Material / Herramienta:", materiales)
        desc_libre = st.text_input("Detalle extra (opcional):")
        detalle = mat_elegido
        if desc_libre:
            detalle += f" - {desc_libre}"
    else: 
        st.markdown("### 🟡 Gasto Personal")
        personales = ["Almuerzo", "Desayuno", "Cena", "Agua / Gaseosa", "Bebidas", "Pasajes / Movilidad", "Cochera", "Recarga de celular", "Farmacia", "Ropa", "Regalos / Varios"]
        per_elegido = st.selectbox("Categoría Personal:", personales)
        desc_libre = st.text_input("Detalle extra (opcional):")
        detalle = per_elegido
        if desc_libre:
            detalle += f" - {desc_libre}"

    col_monto, col_medio = st.columns(2)
    with col_monto:
        monto = st.number_input("Monto Total ($ / S/):", min_value=0.0, step=1.0, format="%.2f")
    with col_medio:
        medio_pago = st.selectbox("Medio de Pago / Cobro:", ["Efectivo", "Digital (Yape / Banco)"])
    
    enviado = st.form_submit_button("Guardar Registro")
    if enviado:
        if monto <= 0:
            st.error("Por favor ingresa un monto válido mayor a 0.")
        else:
            now = datetime.now()
            nueva_op = {
                "fecha": now.strftime("%d/%m/%Y"),
                "mes_anio": now.strftime("%m/%Y"),
                "tipo": tipo,
                "detalle": detalle,
                "medio": medio_pago,
                "monto": monto
            }
            st.session_state.operaciones.insert(0, nueva_op)
            df_temp = pd.DataFrame(st.session_state.operaciones)
            ti = df_temp[df_temp['tipo'].str.contains("Orden de Trabajo")]['monto'].sum() if not df_temp.empty else 0
            tgt = df_temp[df_temp['tipo'].str.contains("Gastos Materiales")]['monto'].sum() if not df_temp.empty else 0
            tgp = df_temp[df_temp['tipo'].str.contains("Gastos Personales")]['monto'].sum() if not df_temp.empty else 0
            gn = ti - (tgt + tgp)
            ef_m = sum([float(r['monto']) if "Orden de Trabajo" in r['tipo'] else -float(r['monto']) for _, r in df_temp.iterrows() if "Efectivo" in r['medio']]) if not df_temp.empty else 0
            dg_m = sum([float(r['monto']) if "Orden de Trabajo" in r['tipo'] else -float(r['monto']) for _, r in df_temp.iterrows() if "Digital" in r['medio']]) if not df_temp.empty else 0
            st_tot = (st.session_state.efectivo_base + ef_m) + (st.session_state.digital_base + dg_m)
            guardar_datos_excel(st.session_state.operaciones, ti, tgt, tgp, gn, st_tot)
            st.success("¡Guardado exitosamente!")
            st.rerun()

df = pd.DataFrame(st.session_state.operaciones)
total_ingresos, total_gastos_taller, total_gastos_personal = 0.0, 0.0, 0.0
efectivo_neto_movs, digital_neto_movs = 0.0, 0.0

if not df.empty and 'tipo' in df.columns and 'monto' in df.columns:
    total_ingresos = df[df['tipo'].str.contains("Orden de Trabajo", na=False)]['monto'].sum()
    total_gastos_taller = df[df['tipo'].str.contains("Gastos Materiales", na=False)]['monto'].sum()
    total_gastos_personal = df[df['tipo'].str.contains("Gastos Personales", na=False)]['monto'].sum()
    for _, row in df.iterrows():
        es_ingreso = "Orden de Trabajo" in str(row.get('tipo', ''))
        valor = float(row.get('monto', 0)) if es_ingreso else -float(row.get('monto', 0))
        if "Efectivo" in str(row.get('medio', '')):
            efectivo_neto_movs += valor
        else:
            digital_neto_movs += valor

total_gastos_general = total_gastos_taller + total_gastos_personal
ganancia_neta = total_ingresos - total_gastos_general
efectivo_actual = st.session_state.efectivo_base + efectivo_neto_movs
digital_actual = st.session_state.digital_base + digital_neto_movs
saldo_total_libre = efectivo_actual + digital_actual

# 📊 CUADROS DE RESUMEN GENERAL
st.markdown("### 📈 Cuadro General Financiero")
col_g1, col_g2 = st.columns(2)
with col_g1:
    st.metric("🟢 Total Ingresos (Autos)", f"${total_ingresos:.2f}")
    st.metric("🔴 Total Gastos Taller", f"${total_gastos_taller:.2f}")
with col_g2:
    st.metric("🟡 Total Gastos Personales", f"${total_gastos_personal:.2f}")
    st.metric("💰 Ganancia Neta Real", f"${ganancia_neta:.2f}")

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

# 📅 HISTORIAL POR DÍA Y VISTAS
filtro_tiempo = st.radio("Seleccionar Historial:", ["📅 Ver Historial de Hoy", "📊 Ver Historial del Mes", "📋 Ver Todo el Historial"], horizontal=True)
fecha_hoy = datetime.now().strftime("%d/%m/%Y")
mes_actual = datetime.now().strftime("%m/%Y")

if not df.empty and 'fecha' in df.columns:
    if "Hoy" in filtro_tiempo:
        df_filtrado = df[df['fecha'] == fecha_hoy]
        st.subheader("📅 Historial y Trabajos de Hoy")
    elif "Mes" in filtro_tiempo:
        df_filtrado = df[df['mes_anio'] == mes_actual] if 'mes_anio' in df.columns else df
        st.subheader("📊 Historial del Mes")
    else:
        df_filtrado = df
        st.subheader("📋 Historial Completo de Todos los Días")

    f_ingresos = df_filtrado[df_filtrado['tipo'].str.contains("Orden de Trabajo", na=False)]['monto'].sum() if not df_filtrado.empty else 0
    f_g_taller = df_filtrado[df_filtrado['tipo'].str.contains("Materiales", na=False)]['monto'].sum() if not df_filtrado.empty else 0
    f_g_personal = df_filtrado[df_filtrado['tipo'].str.contains("Gastos Personales", na=False)]['monto'].sum() if not df_filtrado.empty else 0
    f_ganancia_periodo = f_ingresos - (f_g_taller + f_g_personal)

    col1, col2, col3 = st.columns(3)
    col1.metric("Ingresos en este bloque", f"${f_ingresos:.2f}")
    col2.metric("Gastos en este bloque", f"${(f_g_taller + f_g_personal):.2f}")
    col3.metric("Ganancia del bloque", f"${f_ganancia_periodo:.2f}")

    st.write("---")
    
    # Renderizado en tarjetas limpias tipo cuadro
    for index, row in df_filtrado.iterrows():
        t_val = str(row.get('tipo', ''))
        if "Orden de Trabajo" in t_val:
            clase, signo, cat = "card-orden", "+", "🚗 Orden de Auto"
        elif "Materiales" in t_val:
            clase, signo, cat = "card-taller", "-", "🔴 Insumo Taller"
        else:
            clase, signo, cat = "card-personal", "-", "🟡 Gasto Personal"

        medio_icono = "💵" if "Efectivo" in str(row.get('medio', '')) else "📱"
        st.markdown(f"""
            <div class="{clase}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>{row.get('detalle', '')}</strong><br>
                        <small><b>{cat}</b> ({medio_icono} {row.get('medio', '')}) | 📅 <b>{row.get('fecha', '')}</b></small>
                    </div>
                    <div style="font-size: 1.1rem; font-weight: bold;">
                        {signo}${float(row.get('monto', 0)):.2f}
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.write("---")
    st.subheader("🖨️ Descargar Cuadro Completo en Excel")
    output = io.BytesIO()
    try:
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_export = df.copy()
            df_export.columns = ["Fecha", "MesAnio", "Tipo", "Detalle", "Medio", "Monto"]
            df_export.to_excel(writer, sheet_name="Operaciones", index=False)
            df_resumen_dl = pd.DataFrame({
                "Concepto": ["Total Ingresos", "Total Gastos Taller", "Total Gastos Personal", "Gasto Total General", "Ganancia Neta Real", "Dinero Disponible Total"],
                "Monto ($ / S/)": [total_ingresos, total_gastos_taller, total_gastos_personal, total_gastos_general, ganancia_neta, saldo_total_libre]
            })
            df_resumen_dl.to_excel(writer, sheet_name="Resumen_Financiero", index=False)
        processed_data = output.getvalue()
        st.download_button(
            label="📥 Descargar Excel con Todo el Historial",
            data=processed_data,
            file_name="Reporte_Financiero_Taller.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception:
        st.warning("⚠️ Asegúrate de incluir 'openpyxl' en tu archivo requirements.txt.")
else:
    st.info("No hay registros todavía. Todo está listo para empezar a registrar.")

# ⚙️ ADMINISTRAR Y CORREGIR
st.write("---")
st.markdown("""
    <div class="admin-box">
        <h3 style="margin-top:0; color: #e11d48;">⚙️ Administrar y Corregir Registros</h3>
        <p style="color: #334155; font-size: 0.95rem;">Selecciona la operación que deseas eliminar si hubo algún error.</p>
    </div>
""", unsafe_allow_html=True)

if not df.empty and 'fecha' in df.columns and 'detalle' in df.columns:
    opciones_borrar = [(idx, f"[{row.get('fecha','')}] {row.get('detalle','')} - ${float(row.get('monto',0)):.2f} ({row.get('medio','')})") for idx, row in df.iterrows()]
    seleccion_a_borrar = st.selectbox("Selecciona el registro a eliminar:", options=[item[0] for item in opciones_borrar], format_func=lambda x: next(item[1] for item in opciones_borrar if item[0] == x))
    
    if st.button("🗑️ Eliminar Registro", type="primary"):
        st.session_state.operaciones.pop(seleccion_a_borrar)
        guardar_datos_excel(st.session_state.operaciones, total_ingresos, total_gastos_taller, total_gastos_personal, ganancia_neta, saldo_total_libre)
        st.success("¡Registro eliminado correctamente!")
        st.rerun()
else:
    st.info("No hay registros para corregir.")

# 🔒 CIERRE DE CAJA Y ENVÍO A WHATSAPP
st.write("---")
st.markdown("""
    <div class="cierre-box">
        <h3 style="margin-top:0; color: #0284c7;">🔒 Cierre de Caja Diario y Envío a WhatsApp</h3>
        <p style="color: #334155; font-size: 0.95rem;">Elige a qué número de celular deseas enviar el reporte del cierre de caja:</p>
    </div>
""", unsafe_allow_html=True)

numero_elegido = st.radio("Enviar reporte al número de:", [
    "📱 César 1: +51 984 116 361", 
    "📱 César 2: +51 951 290 168"
], horizontal=True)

telefono_destino = "51984116361" if "984" in numero_elegido else "51951290168"
df_hoy_wa = df[df['fecha'] == fecha_hoy] if not df.empty and 'fecha' in df.columns else pd.DataFrame()

if not df_hoy_wa.empty:
    f_ing_hoy = df_hoy_wa[df_hoy_wa['tipo'].str.contains("Orden de Trabajo", na=False)]['monto'].sum()
    f_gt_hoy = df_hoy_wa[df_hoy_wa['tipo'].str.contains("Materiales", na=False)]['monto'].sum()
    f_gp_hoy = df_hoy_wa[df_hoy_wa['tipo'].str.contains("Gastos Personales", na=False)]['monto'].sum()
    f_gastos_hoy = f_gt_hoy + f_gp_hoy
    f_ganancia_hoy = f_ing_hoy - f_gastos_hoy
    
    msg = "🔒 *CIERRE DE CAJA DIARIO - TALLER CÉSAR BETO*\n"
    msg += "📅 Fecha: " + fecha_hoy + "\n\n"
    msg += "🟢 Total Ingresos (Autos): $" + f"{f_ing_hoy:.2f}\n"
    msg += "🔴 Total Gastos: $" + f"{f_gastos_hoy:.2f}\n"
    msg += "💰 Ganancia Neta: $" + f"{f_ganancia_hoy:.2f}\n\n"
    msg += "Efectivo actual: $" + f"{efectivo_actual:.2f}\n"
    msg += "Digital actual: $" + f"{digital_actual:.2f}\n"
    msg += "Dinero Total Disponible: $" + f"{saldo_total_libre:.2f}\n\n"
    msg += "📋 Detalle de hoy:\n"
    
    for index, row in df_hoy_wa.iterrows():
        signo = "+" if "Orden de Trabajo" in str(row.get('tipo', '')) else "-"
        medio_txt = "Efectivo" if "Efectivo" in str(row.get('medio', '')) else "Digital"
        msg += "• " + str(row.get('detalle', '')) + " (" + medio_txt + "): " + signo + "$" + f"{float(row.get('monto', 0)):.2f}\n"
    
    mensaje_codificado = urllib.parse.quote(msg)
    url_whatsapp = f"https://api.whatsapp.com/send?phone={telefono_destino}&text=" + mensaje_codificado
    
    st.markdown(f'''
        <a href="{url_whatsapp}" target="_blank" class="btn-whatsapp">
            💬 Enviar Cierre de Hoy al WhatsApp seleccionado ({telefono_destino})
        </a>
    ''', unsafe_allow_html=True)
else:
    st.info("💡 Registra al menos una orden o movimiento el día de hoy para habilitar el Cierre de Caja y el envío a WhatsApp.")
