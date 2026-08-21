import csv
from datetime import datetime
import os
import pandas as pd
import streamlit as st

# Configuración de página con diseño moderno
st.set_page_config(
    page_title="Sistema de Gestión Escolar",
    page_icon="🏫",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Estilo visual moderno, limpio e intuitivo (Tarjetas, sombras suaves y bordes redondeados)
st.markdown(
    """
<style>
    /* Estilos generales */
    .stApp {
        background-color: #f4f6f9;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Encabezados y títulos */
    h1, h2, h3 {
        color: #1e293b !important;
        font-weight: 700 !important;
    }
    p, label, span {
        color: #334155 !important;
    }

    /* Botones modernos */
    .stButton>button {
        border-radius: 10px !important;
        background-color: #2563eb !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 0.6rem 1.2rem !important;
        transition: all 0.2s ease-in-out !important;
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2) !important;
    }
    .stButton>button:hover {
        background-color: #1d4ed8 !important;
        box-shadow: 0 4px 8px rgba(37, 99, 235, 0.3) !important;
        transform: translateY(-1px);
    }

    /* Inputs y selecciones */
    .stTextInput input, .stSelectbox select {
        border-radius: 8px !important;
        border: 1px solid #cbd5e1 !important;
        padding: 0.5rem !important;
        background-color: #ffffff !important;
        color: #0f172a !important;
    }

    /* Tablas y contenedores */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
</style>
""",
    unsafe_allow_html=True,
)

CARPETA_CURSOS = "cursos"
CARPETA_ASISTENCIA = "asistencia"
CONTRASEÑA_CORRECTA = "facu2013"

# --- INICIALIZACIÓN DE ESTADOS DE NAVEGACIÓN ---
if "autenticado" not in st.session_state:
  st.session_state.autenticado = False
if "pantalla" not in st.session_state:
  st.session_state.pantalla = "inicio"


def cambiar_pantalla(nombre_pantalla):
  st.session_state.pantalla = nombre_pantalla
  st.rerun()


def leer_alumnos_curso(anio, division):
  ruta = os.path.join(CARPETA_CURSOS, f"{anio}_{division}.csv")
  if not os.path.exists(ruta):
    return None
  try:
    df = pd.read_csv(ruta, sep=None, engine="python", encoding="utf-8-sig")
    df.columns = [c.strip().lower() for c in df.columns]
    return df
  except Exception:
    return None


# ==========================================
# PANTALLA 0: LOGIN / ACCESO DE SEGURIDAD
# ==========================================
if not st.session_state.autenticado:
  st.markdown("### 🔒 Control de Acceso")
  with st.container(border=True):
    st.write("Ingrese la clave para ingresar al sistema escolar.")
    clave = st.text_input(
        "Contraseña:", type="password", placeholder="••••••••"
    )
    if st.button("Iniciar Sesión", use_container_width=True):
      if clave == CONTRASEÑA_CORRECTA:
        st.session_state.autenticado = True
        st.session_state.pantalla = "inicio"
        st.rerun()
      else:
        st.error("Contraseña incorrecta. Intente nuevamente.")
  st.stop()

# --- MENÚ LATERAL PERMANENTE ---
with st.sidebar:
  st.title("🏫 Gestión Escolar")
  st.caption("Sistema de Administración")
  st.divider()

  if st.button("🏠 Inicio", use_container_width=True):
    cambiar_pantalla("inicio")
  if st.button("📋 Tomar Asistencia", use_container_width=True):
    cambiar_pantalla("tomar_asistencia")
  if st.button("📊 Ver / Editar Asistencia", use_container_width=True):
    cambiar_pantalla("ver_asistencia")
  if st.button("🔍 Buscar Alumnos", use_container_width=True):
    cambiar_pantalla("buscar_alumnos")
  if st.button("🚪 Registrar Retiro Antes", use_container_width=True):
    cambiar_pantalla("registrar_retiro")
  if st.button("📄 Historial de Retiros", use_container_width=True):
    cambiar_pantalla("ver_retiros")

  st.divider()
  if st.button("🔒 Cerrar Sesión", use_container_width=True):
    st.session_state.autenticado = False
    st.rerun()

# ==========================================
# PANTALLA 1: INICIO / DASHBOARD
# ==========================================
if st.session_state.pantalla == "inicio":
  st.title("Panel Principal")
  st.write("Seleccione una de las siguientes opciones para trabajar:")

  col1, col2 = st.columns(2)
  with col1:
    with st.container(border=True):
      st.subheader("📋 Asistencia")
      st.write("Tome la asistencia diaria o consulte y modifique las listas.")
      if st.button("Tomar Asistencia", key="btn1"):
        cambiar_pantalla("tomar_asistencia")

    with st.container(border=True):
      st.subheader("🔍 Alumnos")
      st.write("Buscador general de alumnos matriculados por año y división.")
      if st.button("Buscar Alumno", key="btn3"):
        cambiar_pantalla("buscar_alumnos")

  with col2:
    with st.container(border=True):
      st.subheader("🚪 Retiros Anticipados")
      st.write("Registre las salidas anticipadas de los alumnos.")
      if st.button("Registrar Retiro", key="btn2"):
        cambiar_pantalla("registrar_retiro")

    with st.container(border=True):
      st.subheader("📄 Historial")
      st.write("Consulte el registro de retiros con datos de adultos responsables.")
      if st.button("Ver Retiros", key="btn4"):
        cambiar_pantalla("ver_retiros")

# ==========================================
# PANTALLA 2: TOMAR ASISTENCIA
# ==========================================
elif st.session_state.pantalla == "tomar_asistencia":
  st.title("📋 Tomar Asistencia")

  with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
      anio = st.text_input("Año:").strip()
    with col2:
      division = st.text_input("División:").strip()

  if anio and division:
    df_alumnos = leer_alumnos_curso(anio, division)
    if df_alumnos is None:
      st.error(f"No se encontró el curso {anio}° {division}ª.")
    elif df_alumnos.empty:
      st.warning("El curso no posee alumnos cargados.")
    else:
      fecha_act = datetime.now().strftime("%d/%m/%Y")
      st.subheader(f"Curso: {anio}° {division}ª — Fecha: {fecha_act}")

      asistencias = {}
      with st.form("form_tomar_asistencia"):
        for _, row in df_alumnos.iterrows():
          nom_comp = (
              f"{row.get('apellido', '')}, {row.get('nombre', '')}".title()
          )
          asistencias[nom_comp] = st.radio(
              f"**{nom_comp}**",
              ["Presente", "Ausente", "Tarde"],
              horizontal=True,
              key=nom_comp,
          )
          st.divider()

        if st.form_submit_button(
            "Guardar Asistencia Completa", use_container_width=True
        ):
          if not os.path.exists(CARPETA_ASISTENCIA):
            os.makedirs(CARPETA_ASISTENCIA)

          ruta_asis = os.path.join(
              CARPETA_ASISTENCIA, f"asistencia_{anio}_{division}.csv"
          )
          existe = os.path.exists(ruta_asis)

          nuevos_reg = []
          for _, row in df_alumnos.iterrows():
            ap = row.get("apellido", "")
            nom = row.get("nombre", "")
            key = f"{ap}, {nom}".title()
            nuevos_reg.append({
                "fecha": fecha_act,
                "anio": anio,
                "division": division,
                "apellido": ap,
                "nombre": nom,
                "estado": asistencias[key],
            })

          pd.DataFrame(nuevos_reg).to_csv(
              ruta_asis,
              mode="a",
              sep=";",
              index=False,
              header=not existe,
              encoding="utf-8-sig",
          )
          st.success("¡Asistencia guardada correctamente!")

# ==========================================
# PANTALLA 3: VER / EDITAR ASISTENCIA
# ==========================================
elif st.session_state.pantalla == "ver_asistencia":
  st.title("📊 Consultar / Modificar Asistencia")

  with st.container(border=True):
    col1, col2, col3 = st.columns(3)
    with col1:
      anio = st.text_input("Año:").strip()
    with col2:
      division = st.text_input("División:").strip()
    with col3:
      fecha = st.text_input(
          "Fecha (DD/MM/YYYY):", datetime.now().strftime("%d/%m/%Y")
      ).strip()

  if anio and division:
    ruta = os.path.join(
        CARPETA_ASISTENCIA, f"asistencia_{anio}_{division}.csv"
    )
    if not os.path.exists(ruta):
      st.warning("No hay registros guardados para este curso.")
    else:
      df = pd.read_csv(ruta, sep=";", encoding="utf-8-sig")
      df_fil = df[df["fecha"] == fecha]

      if df_fil.empty:
        st.info(f"No se encontraron registros tomados el {fecha}.")
      else:
        st.dataframe(
            df_fil[["apellido", "nombre", "estado"]], use_container_width=True
        )

        st.subheader("Editar Estado de Alumno")
        with st.container(border=True):
          alumnos_list = (
              df_fil["apellido"] + ", " + df_fil["nombre"]
          ).tolist()
          alum_sel = st.selectbox("Seleccionar Alumno:", alumnos_list)
          nuevo_est = st.selectbox(
              "Nuevo Estado:", ["Presente", "Ausente", "Tarde"]
          )

          if st.button("Actualizar Registro", use_container_width=True):
            ap, nom = [x.strip() for x in alum_sel.split(",")]
            mask = (
                (df["fecha"] == fecha)
                & (df["apellido"] == ap)
                & (df["nombre"] == nom)
            )
            df.loc[mask, "estado"] = nuevo_est
            df.to_csv(ruta, sep=";", index=False, encoding="utf-8-sig")
            st.success("Estado actualizado con éxito.")
            st.rerun()

# ==========================================
# PANTALLA 4: BUSCAR ALUMNOS
# ==========================================
elif st.session_state.pantalla == "buscar_alumnos":
  st.title("🔍 Búsqueda de Alumnos")

  with st.container(border=True):
    busqueda = st.text_input(
        "Ingrese el nombre o apellido del alumno:"
    ).strip().lower()

  if busqueda:
    resultados = []
    if os.path.exists(CARPETA_CURSOS):
      for arch in os.listdir(CARPETA_CURSOS):
        if arch.endswith(".csv") and "_" in arch:
          a, d = arch.replace(".csv", "").split("_")
          df = leer_alumnos_curso(a, d)
          if df is not None:
            for _, r in df.iterrows():
              ap = str(r.get("apellido", ""))
              nom = str(r.get("nombre", ""))
              if busqueda in ap.lower() or busqueda in nom.lower():
                resultados.append(
                    {"Apellido": ap, "Nombre": nom, "Año": a, "División": d}
                )

    if resultados:
      st.dataframe(pd.DataFrame(resultados), use_container_width=True)
    else:
      st.warning("No se encontraron coincidencias en ningún curso.")

# ==========================================
# PANTALLA 5: REGISTRAR RETIRO ANTES
# ==========================================
elif st.session_state.pantalla == "registrar_retiro":
  st.title("🚪 Registro de Retiro Anticipado")

  with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
      anio = st.text_input("Año:").strip()
    with col2:
      division = st.text_input("División:").strip()

  if anio and division:
    df_alumnos = leer_alumnos_curso(anio, division)
    if df_alumnos is None:
      st.error("El curso ingresado no existe.")
    else:
      lista_alumnos = (
          df_alumnos["apellido"] + ", " + df_alumnos["nombre"]
      ).tolist()

      with st.form("form_retiro_anticipado"):
        st.subheader("Datos del Alumno y Retiro")
        alumno_sel = st.selectbox("Seleccione Alumno:", lista_alumnos)

        c1, c2 = st.columns(2)
        with c1:
          f_ret = st.text_input(
              "Fecha del retiro:", datetime.now().strftime("%d/%m/%Y")
          )
        with c2:
          h_ret = st.text_input(
              "Hora del retiro:", datetime.now().strftime("%H:%M")
          )

        st.subheader("Datos del Adulto Responsable")
        adulto_nombre = st.text_input(
            "Nombre y Apellido del Adulto:",
            placeholder="Ej: Juan Pérez",
        )
        adulto_dni = st.text_input(
            "DNI del Adulto:", placeholder="Ej: 30123456"
        )

        motivo = st.text_input("Motivo / Observaciones (Opcional):")

        if st.form_submit_button(
            "Registrar Retiro", use_container_width=True
        ):
          if not adulto_nombre.strip() or not adulto_dni.strip():
            st.error(
                "Debe completar tanto el Nombre como el DNI del adulto"
                " responsable."
            )
          else:
            ap, nom = [x.strip() for x in alumno_sel.split(",")]
            ruta_ret = os.path.join(CARPETA_ASISTENCIA, "retiros.csv")
            existe = os.path.exists(ruta_ret)

            nuevo_registro = pd.DataFrame([{
                "fecha": f_ret,
                "hora": h_ret,
                "anio": anio,
                "division": division,
                "apellido": ap,
                "nombre": nom,
                "adulto_nombre": adulto_nombre.strip(),
                "adulto_dni": adulto_dni.strip(),
                "motivo": motivo.strip(),
            }])

            if not os.path.exists(CARPETA_ASISTENCIA):
              os.makedirs(CARPETA_ASISTENCIA)

            nuevo_registro.to_csv(
                ruta_ret,
                mode="a",
                sep=";",
                index=False,
                header=not existe,
                encoding="utf-8-sig",
            )
            st.success(
                f"Retiro guardado: {ap}, {nom} retirado por {adulto_nombre}"
                f" (DNI: {adulto_dni})."
            )

# ==========================================
# PANTALLA 6: VER / EDITAR RETIROS
# ==========================================
elif st.session_state.pantalla == "ver_retiros":
  st.title("📄 Historial de Retiros Anticipados")

  ruta_ret = os.path.join(CARPETA_ASISTENCIA, "retiros.csv")

  if not os.path.exists(ruta_ret):
    st.info("No hay registros de retiros guardados.")
  else:
    df_ret = pd.read_csv(ruta_ret, sep=";", encoding="utf-8-sig")

    st.dataframe(df_ret, use_container_width=True)

    st.subheader("Eliminar un registro")
    with st.container(border=True):
      idx_elim = st.number_input(
          "Ingrese la fila (índice) a borrar:",
          min_value=0,
          max_value=len(df_ret) - 1,
          step=1,
      )
      if st.button("Eliminar Registro", use_container_width=True):
        df_ret = df_ret.drop(idx_elim)
        df_ret.to_csv(ruta_ret, sep=";", index=False, encoding="utf-8-sig")
        st.success("Registro eliminado del historial.")
        st.rerun()