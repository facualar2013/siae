from datetime import datetime
import os
import pandas as pd
import streamlit as st

# Configuración adaptada a pantallas móviles
st.set_page_config(
    page_title="Sistema Escolar",
    page_icon="🏫",
    layout="centered",
    initial_sidebar_state="collapsed",
)

CARPETA_CURSOS = "cursos"
CARPETA_ASISTENCIA = "asistencia"
CONTRASEÑA_CORRECTA = "facu2013"


def inicializar_carpetas():
  if not os.path.exists(CARPETA_CURSOS):
    os.makedirs(CARPETA_CURSOS)
  if not os.path.exists(CARPETA_ASISTENCIA):
    os.makedirs(CARPETA_ASISTENCIA)


def cargar_csv_curso(ruta):
  if not os.path.exists(ruta):
    return None
  try:
    df = pd.read_csv(ruta, sep=None, engine="python", encoding="utf-8-sig")
    df.columns = [str(c).strip().lower() for c in df.columns]
    return df
  except Exception as e:
    st.error(f"Error al leer el archivo: {e}")
    return None


def obtener_columna(df, nombre_buscado):
  for col in df.columns:
    if col.strip().lower() == nombre_buscado.lower():
      return col
  return None


# --- CONTROL DE ACCESO ---
if "autenticado" not in st.session_state:
  st.session_state["autenticado"] = False

inicializar_carpetas()

if not st.session_state["autenticado"]:
  st.title("🔒 Control de Acceso")
  st.subheader("SISTEMA INTEGRAL DE ADMINISTRACIÓN ESCOLAR")

  clave = st.text_input(
      "Ingrese la contraseña de seguridad:", type="password"
  )

  if st.button("Ingresar", use_container_width=True):
    if clave.strip() == CONTRASEÑA_CORRECTA:
      st.session_state["autenticado"] = True
      st.success("Acceso concedido.")
      st.rerun()
    else:
      st.error("Contraseña incorrecta.")
  st.stop()

# --- CABECERA Y NAVEGACIÓN PRINCIPAL ---
col_titulo, col_logout = st.columns([3, 1])
with col_titulo:
  st.title("🏫 Sistema Escolar")
with col_logout:
  st.write("")
  if st.button("🚪 Salir", use_container_width=True):
    st.session_state["autenticado"] = False
    st.rerun()

# Pestañas superiores
tab_alumnos, tab_asistencia = st.tabs(["📋 Alumnos", "📝 Asistencia"])

# ==========================================
# PESTAÑA 1: ALUMNOS
# ==========================================
with tab_alumnos:
  st.header("Sección Alumnos")
  sub_opcion = st.radio(
      "Método de búsqueda:",
      ["Por año y división", "Por nombre / apellido"],
      horizontal=True,
  )

  if sub_opcion == "Por año y división":
    col1, col2 = st.columns(2)
    with col1:
      anio = st.text_input("Año (ej. 1):", key="al_anio")
    with col2:
      division = st.text_input("División (ej. 1):", key="al_div")

    if st.button("🔍 Buscar Curso", use_container_width=True):
      if anio and division:
        ruta = os.path.join(
            CARPETA_CURSOS, f"{anio.strip()}_{division.strip()}.csv"
        )
        df = cargar_csv_curso(ruta)
        if df is not None:
          st.success(f"Lista de Alumnos - {anio}° {division}ª")
          col_ap = obtener_columna(df, "apellido")
          col_nom = obtener_columna(df, "nombre")
          if col_ap and col_nom:
            df_mostrar = df[[col_ap, col_nom]].rename(
                columns={col_ap: "Apellido", col_nom: "Nombre"}
            )
            df_mostrar.index = df_mostrar.index + 1
            st.dataframe(df_mostrar, use_container_width=True)
          else:
            st.warning("El archivo CSV no tiene columnas de apellido/nombre.")
        else:
          st.error(f"No se encontró el curso {anio}° {division}ª.")
      else:
        st.warning("Ingrese año y división.")

  elif sub_opcion == "Por nombre / apellido":
    busqueda = st.text_input("Buscar por nombre o apellido:").strip().lower()

    if st.button("🔍 Buscar Alumno", use_container_width=True):
      if busqueda:
        coincidencias = []
        for archivo in os.listdir(CARPETA_CURSOS):
          if archivo.endswith(".csv") and "_" in archivo:
            partes = archivo.replace(".csv", "").split("_")
            if len(partes) == 2:
              anio, div = partes
              ruta = os.path.join(CARPETA_CURSOS, archivo)
              df = cargar_csv_curso(ruta)
              if df is not None:
                col_ap = obtener_columna(df, "apellido")
                col_nom = obtener_columna(df, "nombre")
                if col_ap and col_nom:
                  for _, row in df.iterrows():
                    ap = str(row[col_ap]).strip()
                    nom = str(row[col_nom]).strip()
                    if busqueda in ap.lower() or busqueda in nom.lower():
                      coincidencias.append({
                          "Apellido": ap,
                          "Nombre": nom,
                          "Año": f"{anio}°",
                          "División": f"{div}ª",
                      })

        if coincidencias:
          res_df = pd.DataFrame(coincidencias)
          res_df.index = res_df.index + 1
          st.success(f"Se encontraron {len(coincidencias)} resultado(s):")
          st.dataframe(res_df, use_container_width=True)
        else:
          st.info("No se encontraron coincidencias.")
      else:
        st.warning("Ingrese un término de búsqueda.")

# ==========================================
# PESTAÑA 2: ASISTENCIA
# ==========================================
with tab_asistencia:
  st.header("Sección Asistencia")
  sub_opcion_asist = st.radio(
      "Acción:",
      ["Tomar asistencia", "Editar asistencia"],
      horizontal=True,
  )

  # --- TOMAR ASISTENCIA ---
  if sub_opcion_asist == "Tomar asistencia":
    col1, col2 = st.columns(2)
    with col1:
      anio = st.text_input("Año:", key="ta_anio")
    with col2:
      division = st.text_input("División:", key="ta_div")

    fecha_sel = st.date_input("Fecha:", value=datetime.now())

    if anio and division:
      ruta_curso = os.path.join(
          CARPETA_CURSOS, f"{anio.strip()}_{division.strip()}.csv"
      )
      df_curso = cargar_csv_curso(ruta_curso)

      if df_curso is not None:
        col_ap = obtener_columna(df_curso, "apellido")
        col_nom = obtener_columna(df_curso, "nombre")

        if col_ap and col_nom:
          st.subheader(
              f"Curso: {anio}° {division}ª - {fecha_sel.strftime('%d/%m/%Y')}"
          )

          df_asistencia = pd.DataFrame({
              "Apellido": df_curso[col_ap].astype(str).str.strip(),
              "Nombre": df_curso[col_nom].astype(str).str.strip(),
              "Estado": ["Presente"] * len(df_curso),
          })

          st.write("Seleccione el estado de cada alumno:")
          df_editado = st.data_editor(
              df_asistencia,
              column_config={
                  "Estado": st.column_config.SelectboxColumn(
                      "Estado",
                      options=["Presente", "Ausente", "Tarde"],
                      required=True,
                  )
              },
              disabled=["Apellido", "Nombre"],
              hide_index=True,
              use_container_width=True,
          )

          if st.button("💾 Guardar Asistencia", use_container_width=True):
            fecha_str = fecha_sel.strftime("%d/%m/%Y")
            ruta_asist = os.path.join(
                CARPETA_ASISTENCIA,
                f"asistencia_{anio.strip()}_{division.strip()}.csv",
            )

            df_guardar = df_editado.copy()
            df_guardar.insert(0, "division", division.strip())
            df_guardar.insert(0, "anio", anio.strip())
            df_guardar.insert(0, "fecha", fecha_str)
            df_guardar.columns = [
                "fecha",
                "anio",
                "division",
                "apellido",
                "nombre",
                "estado",
            ]

            if os.path.exists(ruta_asist):
              df_existente = pd.read_csv(
                  ruta_asist, sep=";", encoding="utf-8-sig"
              )
              df_existente = df_existente[df_existente["fecha"] != fecha_str]
              df_final = pd.concat(
                  [df_existente, df_guardar], ignore_index=True
              )
            else:
              df_final = df_guardar

            df_final.to_csv(
                ruta_asist, sep=";", index=False, encoding="utf-8-sig"
            )

            cant_p = (df_editado["Estado"] == "Presente").sum()
            cant_a = (df_editado["Estado"] == "Ausente").sum()
            cant_t = (df_editado["Estado"] == "Tarde").sum()

            st.success("¡Asistencia guardada!")
            st.info(
                f"📊 **Resumen:** P: {cant_p} | A: {cant_a} | T: {cant_t} |"
                f" Total: {len(df_editado)}"
            )
        else:
          st.error("Columnas de apellido/nombre no encontradas.")
      else:
        st.warning(f"No se encontró el curso {anio}° {division}ª.")

  # --- EDITAR ASISTENCIA ---
  elif sub_opcion_asist == "Editar asistencia":
    col1, col2 = st.columns(2)
    with col1:
      anio = st.text_input("Año:", key="ed_anio")
    with col2:
      division = st.text_input("División:", key="ed_div")

    fecha_sel = st.date_input("Fecha a editar:", value=datetime.now())

    if anio and division:
      fecha_str = fecha_sel.strftime("%d/%m/%Y")
      ruta_asist = os.path.join(
          CARPETA_ASISTENCIA,
          f"asistencia_{anio.strip()}_{division.strip()}.csv",
      )

      if os.path.exists(ruta_asist):
        df_todas = pd.read_csv(ruta_asist, sep=";", encoding="utf-8-sig")
        df_fecha = df_todas[df_todas["fecha"] == fecha_str].copy()

        if not df_fecha.empty:
          st.subheader(f"Editando {anio}° {division}ª - {fecha_str}")

          df_mostrar = df_fecha[["apellido", "nombre", "estado"]].rename(
              columns={
                  "apellido": "Apellido",
                  "nombre": "Nombre",
                  "estado": "Estado",
              }
          )

          df_editado = st.data_editor(
              df_mostrar,
              column_config={
                  "Estado": st.column_config.SelectboxColumn(
                      "Estado",
                      options=["Presente", "Ausente", "Tarde"],
                      required=True,
                  )
              },
              disabled=["Apellido", "Nombre"],
              hide_index=True,
              use_container_width=True,
          )

          if st.button("💾 Guardar Cambios", use_container_width=True):
            df_todas.loc[df_todas["fecha"] == fecha_str, "estado"] = df_editado[
                "Estado"
            ].values
            df_todas.to_csv(
                ruta_asist, sep=";", index=False, encoding="utf-8-sig"
            )
            st.success("Cambios guardados correctamente.")

          if st.button("🗑️ Borrar Día", use_container_width=True):
            df_resto = df_todas[df_todas["fecha"] != fecha_str]
            df_resto.to_csv(
                ruta_asist, sep=";", index=False, encoding="utf-8-sig"
            )
            st.warning(f"Se borraron los registros del {fecha_str}.")
            st.rerun()

        else:
          st.info(f"Sin registros guardados para el {fecha_str}.")
      else:
        st.warning(f"No hay historial de asistencia para {anio}° {division}ª.")