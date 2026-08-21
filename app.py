import csv
from datetime import datetime
import os
import pandas as pd
import streamlit as st

# Configuración de página
st.set_page_config(
    page_title="Sistema de Gestión Escolar",
    page_icon="🏫",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Estilos CSS institucionales y ajuste visual
st.markdown(
    """
<style>
    .stApp {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Botones de menú de alto contraste */
    div.stButton > button {
        background-color: #1d4ed8 !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        width: 100% !important;
    }
    div.stButton > button:hover {
        background-color: #1e40af !important;
        color: #ffffff !important;
    }
    div.stButton > button p, div.stButton > button span {
        color: #ffffff !important;
    }

    /* Estilo para los menús desplegables de la barra lateral */
    [data-testid="stSidebar"] .stExpander {
        border: 1px solid #3b82f6 !important;
        border-radius: 8px !important;
        margin-bottom: 0.5rem !important;
        background-color: rgba(29, 78, 216, 0.05) !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

CARPETA_CURSOS = "cursos"
CARPETA_ASISTENCIA = "asistencia"
CONTRASEÑA_CORRECTA = "facu2013"

# --- NAVEGACIÓN ---
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


# --- CONTROL DE ACCESO ---
if not st.session_state.autenticado:
  st.title("🔒 Control de Acceso")
  with st.container(border=True):
    clave = st.text_input("Ingrese la contraseña:", type="password")
    if st.button("Ingresar al Sistema", use_container_width=True):
      if clave == CONTRASEÑA_CORRECTA:
        st.session_state.autenticado = True
        st.session_state.pantalla = "inicio"
        st.rerun()
      else:
        st.error("Contraseña incorrecta.")
  st.stop()

# ==========================================
# MENÚ LATERAL
# ==========================================
with st.sidebar:
  st.title("🏫 Gestión Escolar")
  st.caption("Menú de Navegación")
  st.divider()

  # 1. Inicio
  if st.button("🏠 Inicio", use_container_width=True):
    cambiar_pantalla("inicio")

  # 2. Alumnos
  if st.button("👥 Alumnos", use_container_width=True):
    cambiar_pantalla("alumnos")

  # 3. Asistencia (Submenús)
  with st.expander(
      "📋 **Asistencia**",
      expanded=(
          st.session_state.pantalla in ["tomar_asistencia", "ver_asistencia"]
      ),
  ):
    if st.button("📝 Tomar Asistencia", use_container_width=True):
      cambiar_pantalla("tomar_asistencia")
    if st.button("📊 Ver / Editar Asistencia", use_container_width=True):
      cambiar_pantalla("ver_asistencia")

  # 4. Retiros Anticipados (Submenús)
  with st.expander(
      "🚪 **Retiros Anticipados**",
      expanded=(st.session_state.pantalla in ["registrar_retiro", "ver_retiros"]),
  ):
    if st.button("📝 Registrar Retiro Antes", use_container_width=True):
      cambiar_pantalla("registrar_retiro")
    if st.button("📄 Historial de Retiros", use_container_width=True):
      cambiar_pantalla("ver_retiros")

  st.divider()
  if st.button("🔒 Cerrar Sesión", use_container_width=True):
    st.session_state.autenticado = False
    st.rerun()

# ==========================================
# PANTALLAS
# ==========================================

# 1. INICIO
if st.session_state.pantalla == "inicio":
  st.title("Panel Central")
  st.write("Seleccione un módulo en el menú lateral para continuar.")

# 2. ALUMNOS (ESTRUCTURA SOLICITADA)
elif st.session_state.pantalla == "alumnos":
  st.title("👥 Alumnos")

  # Menú Principal: Buscar / Editar Alumnos
  tab_buscar, tab_editar = st.tabs(["🔍 Buscar", "✏️ Editar Alumnos"])

  # ----------------------------------------
  # PESTAÑA: BUSCAR
  # ----------------------------------------
  with tab_buscar:
    subtab_b_nombre, subtab_b_curso = st.tabs(
        ["👤 Buscar por Nombre / Apellido", "🏫 Buscar por Año y División"]
    )

    with subtab_b_nombre:
      busqueda = (
          st.text_input(
              "Ingrese el nombre o apellido:", key="b_nom_bus"
          )
          .strip()
          .lower()
      )
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
                    resultados.append({
                        "Apellido": ap.upper(),
                        "Nombre": nom.title(),
                        "Año": a,
                        "División": d,
                    })
        if resultados:
          st.dataframe(
              pd.DataFrame(resultados),
              use_container_width=True,
              hide_index=True,
          )
        else:
          st.warning("No se encontraron coincidencias.")

    with subtab_b_curso:
      col1, col2 = st.columns(2)
      with col1:
        b_anio = st.text_input("Año:", key="b_anio_bus").strip()
      with col2:
        b_div = st.text_input("División:", key="b_div_bus").strip()

      if b_anio and b_div:
        df_curso = leer_alumnos_curso(b_anio, b_div)
        if df_curso is None:
          st.error(f"No se encontró el curso {b_anio}° {b_div}ª.")
        elif df_curso.empty:
          st.warning("El curso seleccionado no contiene alumnos cargados.")
        else:
          st.subheader(f"Nómina del Curso: {b_anio}° {b_div}ª")
          df_mostrar = df_curso.copy()
          df_mostrar["apellido"] = (
              df_mostrar["apellido"].astype(str).str.upper()
          )
          df_mostrar["nombre"] = df_mostrar["nombre"].astype(str).str.title()
          st.dataframe(
              df_mostrar[["apellido", "nombre"]],
              use_container_width=True,
              hide_index=True,
          )

  # ----------------------------------------
  # PESTAÑA: EDITAR ALUMNOS
  # ----------------------------------------
  with tab_editar:
    subtab_e_nombre, subtab_e_curso = st.tabs(
        ["👤 Editar por Nombre / Apellido", "🏫 Editar por Año y División"]
    )

    with subtab_e_nombre:
      busqueda_e = (
          st.text_input(
              "Ingrese el nombre o apellido a editar:", key="e_nom_ed"
          )
          .strip()
          .lower()
      )
      if busqueda_e:
        resultados_e = []
        if os.path.exists(CARPETA_CURSOS):
          for arch in os.listdir(CARPETA_CURSOS):
            if arch.endswith(".csv") and "_" in arch:
              a, d = arch.replace(".csv", "").split("_")
              df = leer_alumnos_curso(a, d)
              if df is not None:
                for idx, r in df.iterrows():
                  ap = str(r.get("apellido", ""))
                  nom = str(r.get("nombre", ""))
                  if busqueda_e in ap.lower() or busqueda_e in nom.lower():
                    resultados_e.append({
                        "Apellido": ap.upper(),
                        "Nombre": nom.title(),
                        "Año": a,
                        "División": d,
                        "_archivo": arch,
                        "_idx": idx,
                    })

        if resultados_e:
          st.info(
              "💡 **Haga doble clic en la celda que desea editar** y presione"
              " el botón 'Guardar Cambios'."
          )
          df_res = pd.DataFrame(resultados_e)

          df_editado_res = st.data_editor(
              df_res[["Apellido", "Nombre", "Año", "División"]],
              use_container_width=True,
              hide_index=True,
              key="editor_busqueda_alumnos",
          )

          if st.button(
              "💾 Guardar Cambios",
              use_container_width=True,
              key="btn_guardar_e_nom",
          ):
            for i, row in df_editado_res.iterrows():
              orig = df_res.iloc[i]
              arch_orig = orig["_archivo"]
              idx_orig = orig["_idx"]

              new_ap = str(row["Apellido"]).strip()
              new_nom = str(row["Nombre"]).strip()
              new_a = str(row["Año"]).strip()
              new_d = str(row["División"]).strip()

              # Si no cambió de curso
              if new_a == orig["Año"] and new_d == orig["División"]:
                ruta = os.path.join(CARPETA_CURSOS, arch_orig)
                df_temp = pd.read_csv(
                    ruta, sep=None, engine="python", encoding="utf-8-sig"
                )
                df_temp.columns = [c.strip().lower() for c in df_temp.columns]
                df_temp.loc[idx_orig, "apellido"] = new_ap
                df_temp.loc[idx_orig, "nombre"] = new_nom
                df_temp.to_csv(ruta, index=False, encoding="utf-8-sig")
              else:
                # Cambió de curso: se remueve del viejo y agrega al nuevo
                ruta_vieja = os.path.join(CARPETA_CURSOS, arch_orig)
                df_viejo = pd.read_csv(
                    ruta_vieja, sep=None, engine="python", encoding="utf-8-sig"
                )
                df_viejo.columns = [c.strip().lower() for c in df_viejo.columns]
                df_viejo = df_viejo.drop(idx_orig)
                df_viejo.to_csv(ruta_vieja, index=False, encoding="utf-8-sig")

                ruta_nueva = os.path.join(CARPETA_CURSOS, f"{new_a}_{new_d}.csv")
                nuevo_reg = pd.DataFrame(
                    [{"apellido": new_ap, "nombre": new_nom}]
                )
                existe_nueva = os.path.exists(ruta_nueva)
                nuevo_reg.to_csv(
                    ruta_nueva,
                    mode="a",
                    index=False,
                    header=not existe_nueva,
                    encoding="utf-8-sig",
                )

            st.success("¡Datos actualizados correctamente!")
            st.rerun()
        else:
          st.warning("No se encontraron coincidencias.")

    with subtab_e_curso:
      col1, col2 = st.columns(2)
      with col1:
        e_anio = st.text_input("Año:", key="e_anio_ed").strip()
      with col2:
        e_div = st.text_input("División:", key="e_div_ed").strip()

      if e_anio and e_div:
        df_curso = leer_alumnos_curso(e_anio, e_div)
        if df_curso is None:
          st.error(f"No se encontró el curso {e_anio}° {e_div}ª.")
        elif df_curso.empty:
          st.warning("El curso seleccionado no contiene alumnos.")
        else:
          st.info(
              "💡 Haga doble clic en los nombres o apellidos para modificarlos"
              " directamente."
          )

          df_edicion = df_curso.copy()
          df_edicion["apellido"] = (
              df_edicion["apellido"].astype(str).str.upper()
          )
          df_edicion["nombre"] = df_edicion["nombre"].astype(str).str.title()

          df_editado = st.data_editor(
              df_edicion[["apellido", "nombre"]],
              column_config={
                  "apellido": st.column_config.TextColumn("Apellido"),
                  "nombre": st.column_config.TextColumn("Nombre"),
              },
              use_container_width=True,
              num_rows="dynamic",
              hide_index=True,
              key=f"editor_curso_{e_anio}_{e_div}",
          )

          if st.button(
              "💾 Guardar Cambios del Curso",
              use_container_width=True,
              key="btn_guardar_curso",
          ):
            ruta = os.path.join(CARPETA_CURSOS, f"{e_anio}_{e_div}.csv")
            df_editado.to_csv(ruta, index=False, encoding="utf-8-sig")
            st.success(f"¡Curso {e_anio}° {e_div}ª actualizado con éxito!")
            st.rerun()

# 3. TOMAR ASISTENCIA
elif st.session_state.pantalla == "tomar_asistencia":
  st.title("📝 Tomar Asistencia")
  col1, col2 = st.columns(2)
  with col1:
    anio = st.text_input("Año:").strip()
  with col2:
    division = st.text_input("División:").strip()

  if anio and division:
    df_alumnos = leer_alumnos_curso(anio, division)
    if df_alumnos is None:
      st.error(f"No existe el curso {anio}° {division}ª.")
    elif df_alumnos.empty:
      st.warning("El curso no posee alumnos cargados.")
    else:
      fecha_act = datetime.now().strftime("%d/%m/%Y")
      st.subheader(f"Curso: {anio}° {division}ª | Fecha: {fecha_act}")

      df_edicion = df_alumnos.copy()
      df_edicion["apellido"] = df_edicion["apellido"].astype(str).str.upper()
      df_edicion["nombre"] = df_edicion["nombre"].astype(str).str.title()
      df_edicion["estado"] = "Presente"

      df_editado = st.data_editor(
          df_edicion[["apellido", "nombre", "estado"]],
          column_config={
              "apellido": st.column_config.TextColumn(
                  "Apellido", disabled=True
              ),
              "nombre": st.column_config.TextColumn("Nombre", disabled=True),
              "estado": st.column_config.SelectboxColumn(
                  "Estado",
                  options=["Presente", "Ausente", "Tarde"],
                  required=True,
              ),
          },
          hide_index=True,
          use_container_width=True,
      )

      if st.button("Guardar Asistencia Completa", use_container_width=True):
        if not os.path.exists(CARPETA_ASISTENCIA):
          os.makedirs(CARPETA_ASISTENCIA)

        ruta_asis = os.path.join(
            CARPETA_ASISTENCIA, f"asistencia_{anio}_{division}.csv"
        )
        existe = os.path.exists(ruta_asis)

        df_guardar = df_editado.copy()
        df_guardar["fecha"] = fecha_act
        df_guardar["anio"] = anio
        df_guardar["division"] = division
        df_guardar = df_guardar[
            ["fecha", "anio", "division", "apellido", "nombre", "estado"]
        ]

        df_guardar.to_csv(
            ruta_asis,
            mode="a",
            sep=";",
            index=False,
            header=not existe,
            encoding="utf-8-sig",
        )
        st.success("¡Asistencia registrada!")

# 4. VER / EDITAR ASISTENCIA
elif st.session_state.pantalla == "ver_asistencia":
  st.title("📊 Consultar / Editar Asistencia")
  col1, col2, col3 = st.columns(3)
  with col1:
    v_anio = st.text_input("Año:").strip()
  with col2:
    v_div = st.text_input("División:").strip()
  with col3:
    v_fecha = st.text_input(
        "Fecha (DD/MM/YYYY):", datetime.now().strftime("%d/%m/%Y")
    ).strip()

  if v_anio and v_div:
    ruta = os.path.join(CARPETA_ASISTENCIA, f"asistencia_{v_anio}_{v_div}.csv")
    if not os.path.exists(ruta):
      st.warning("No hay registros cargados.")
    else:
      df = pd.read_csv(ruta, sep=";", encoding="utf-8-sig")
      df_fil = df[df["fecha"] == v_fecha]

      if df_fil.empty:
        st.info("No hay datos en esta fecha.")
      else:
        df_editado_consulta = st.data_editor(
            df_fil[["apellido", "nombre", "estado"]],
            column_config={
                "apellido": st.column_config.TextColumn(
                    "Apellido", disabled=True
                ),
                "nombre": st.column_config.TextColumn("Nombre", disabled=True),
                "estado": st.column_config.SelectboxColumn(
                    "Estado",
                    options=["Presente", "Ausente", "Tarde"],
                    required=True,
                ),
            },
            hide_index=True,
            use_container_width=True,
        )

        if st.button("Guardar Cambios", use_container_width=True):
          for idx, row in df_editado_consulta.iterrows():
            cond = (
                (df["fecha"] == v_fecha)
                & (df["apellido"] == row["apellido"])
                & (df["nombre"] == row["nombre"])
            )
            df.loc[cond, "estado"] = row["estado"]

          df.to_csv(ruta, sep=";", index=False, encoding="utf-8-sig")
          st.success("Cambios guardados.")
          st.rerun()

# 5. REGISTRAR RETIRO ANTES
elif st.session_state.pantalla == "registrar_retiro":
  st.title("📝 Registrar Retiro Anticipado")
  col1, col2 = st.columns(2)
  with col1:
    r_anio = st.text_input("Año:").strip()
  with col2:
    r_div = st.text_input("División:").strip()

  if r_anio and r_div:
    df_alumnos = leer_alumnos_curso(r_anio, r_div)
    if df_alumnos is None:
      st.error("Curso no encontrado.")
    else:
      lista_alumnos = (
          df_alumnos["apellido"].astype(str).str.upper()
          + ", "
          + df_alumnos["nombre"].astype(str).str.title()
      ).tolist()

      with st.form("form_nuevo_retiro"):
        alumno_sel = st.selectbox("Seleccione Alumno:", lista_alumnos)
        c1, c2 = st.columns(2)
        with c1:
          f_ret = st.text_input("Fecha:", datetime.now().strftime("%d/%m/%Y"))
        with c2:
          h_ret = st.text_input("Hora:", datetime.now().strftime("%H:%M"))

        st.subheader("Adulto Responsable")
        adulto_nombre = st.text_input("Nombre y Apellido:")
        adulto_dni = st.text_input("DNI:")
        motivo = st.text_input("Motivo (Opcional):")

        if st.form_submit_button("Guardar Retiro", use_container_width=True):
          if not adulto_nombre.strip() or not adulto_dni.strip():
            st.error("Nombre y DNI obligatorios.")
          else:
            ap, nom = [x.strip() for x in alumno_sel.split(",")]
            ruta_ret = os.path.join(CARPETA_ASISTENCIA, "retiros.csv")
            existe = os.path.exists(ruta_ret)

            nuevo_reg = pd.DataFrame([{
                "fecha": f_ret,
                "hora": h_ret,
                "anio": r_anio,
                "division": r_div,
                "apellido": ap,
                "nombre": nom,
                "adulto_nombre": adulto_nombre.strip(),
                "adulto_dni": adulto_dni.strip(),
                "motivo": motivo.strip(),
            }])

            if not os.path.exists(CARPETA_ASISTENCIA):
              os.makedirs(CARPETA_ASISTENCIA)

            nuevo_reg.to_csv(
                ruta_ret,
                mode="a",
                sep=";",
                index=False,
                header=not existe,
                encoding="utf-8-sig",
            )
            st.success("Retiro guardado exitosamente.")

# 6. HISTORIAL DE RETIROS
elif st.session_state.pantalla == "ver_retiros":
  st.title("📄 Historial de Retiros")
  ruta_ret = os.path.join(CARPETA_ASISTENCIA, "retiros.csv")

  if not os.path.exists(ruta_ret):
    st.info("Sin registros de retiros.")
  else:
    df_ret = pd.read_csv(ruta_ret, sep=";", encoding="utf-8-sig")
    st.dataframe(df_ret, use_container_width=True)

    st.subheader("Eliminar Registro")
    idx_elim = st.number_input(
        "Fila a borrar:", min_value=0, max_value=len(df_ret) - 1, step=1
    )
    if st.button("Eliminar Registro", use_container_width=True):
      df_ret = df_ret.drop(idx_elim)
      df_ret.to_csv(ruta_ret, sep=";", index=False, encoding="utf-8-sig")
      st.success("Registro eliminado.")
      st.rerun()