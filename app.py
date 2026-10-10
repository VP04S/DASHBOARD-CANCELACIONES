import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from io import BytesIO

# =========================
# CONFIG
# =========================

st.set_page_config(
    page_title="Dashboard Operacional",
    page_icon="📦",
    layout="wide"
)

UPLOAD_PATH = Path("uploads")
UPLOAD_PATH.mkdir(exist_ok=True)

# =========================
# TITLE
# =========================

st.markdown("""
# 📦 Dashboard Operacional
### Seguimiento de Cancelaciones
""")

# =========================
# CARGA DE ARCHIVOS
# =========================

archivo = st.file_uploader(
    "📤 Subir Excel",
    type=["xlsx"]
)

if archivo is not None:

    ruta = UPLOAD_PATH / archivo.name

    with open(ruta, "wb") as f:
        f.write(archivo.getbuffer())

    st.success("✅ Archivo cargado correctamente")

# =========================
# LECTURA
# =========================

archivos = list(UPLOAD_PATH.glob("*.xlsx"))

if len(archivos) > 0:

    dataframes = []

    columnas = [
        "MOTIVO",
        "AREA",
        "SKU",
        "DESCRIPCION",
        "TIENDA",
        "TIPO",
        "PCE",
        "FECHA",
        "REFERENCIA"
    ]

    for file in archivos:

        try:

            df_temp = pd.read_excel(file)

            df_temp.columns = (
                df_temp.columns.astype(str)
                .str.strip()
                .str.upper()
            )

            faltantes = [
                col
                for col in columnas
                if col not in df_temp.columns
            ]

            if faltantes:
                continue

            df_temp = df_temp[columnas]

            dataframes.append(df_temp)

        except:
            pass

    if len(dataframes) == 0:
        st.warning("No existen archivos válidos")
        st.stop()

    df = pd.concat(
        dataframes,
        ignore_index=True
    )

    df["FECHA"] = pd.to_datetime(
        df["FECHA"],
        errors="coerce"
    )

    # =========================
    # SIDEBAR
    # =========================

    st.sidebar.title("🔎 Filtros")

    fecha_min = df["FECHA"].min()
    fecha_max = df["FECHA"].max()

    if pd.notna(fecha_min):

        rango_fecha = st.sidebar.date_input(
            "FECHA",
            value=(
                fecha_min.date(),
                fecha_max.date()
            )
        )

        if len(rango_fecha) == 2:

            inicio, fin = rango_fecha

            df = df[
                (df["FECHA"].dt.date >= inicio)
                &
                (df["FECHA"].dt.date <= fin)
            ]

    motivo = st.sidebar.multiselect(
        "MOTIVO",
        sorted(df["MOTIVO"].dropna().unique())
    )

    area = st.sidebar.multiselect(
        "AREA",
        sorted(df["AREA"].dropna().unique())
    )

sku = st.sidebar.multiselect(
    "SKU",
    sorted(df["SKU"].astype(str).dropna().unique())
)

    tienda = st.sidebar.multiselect(
        "TIENDA",
        sorted(df["TIENDA"].dropna().unique())
    )

    tipo = st.sidebar.multiselect(
        "TIPO",
        sorted(df["TIPO"].dropna().unique())
    )

    referencia = st.sidebar.multiselect(
        "REFERENCIA",
        sorted(df["REFERENCIA"].dropna().unique())
    )

    if motivo:
        df = df[df["MOTIVO"].isin(motivo)]

    if area:
        df = df[df["AREA"].isin(area)]

    if sku:
        df = df[df["SKU"].isin(sku)]

    if tienda:
        df = df[df["TIENDA"].isin(tienda)]

    if tipo:
        df = df[df["TIPO"].isin(tipo)]

    if referencia:
        df = df[df["REFERENCIA"].isin(referencia)]

    # =========================
    # KPI
    # =========================

    c1,c2,c3,c4 = st.columns(4)

    c1.metric(
        "📦 Registros",
        f"{len(df):,}"
    )

    c2.metric(
        "📋 SKU",
        f"{df['SKU'].nunique():,}"
    )

    c3.metric(
        "🏪 Tiendas",
        f"{df['TIENDA'].nunique():,}"
    )

    c4.metric(
        "🏢 Áreas",
        f"{df['AREA'].nunique():,}"
    )

    c5,c6,c7,c8 = st.columns(4)

    c5.metric(
        "📌 Motivos",
        f"{df['MOTIVO'].nunique():,}"
    )

    c6.metric(
        "💰 Total PCE",
        f"{pd.to_numeric(df['PCE'], errors='coerce').sum():,.0f}"
    )

    c7.metric(
        "🔍 Referencias",
        f"{df['REFERENCIA'].nunique():,}"
    )

    c8.metric(
        "📅 Última Fecha",
        str(df["FECHA"].max().date())
        if pd.notna(df["FECHA"].max())
        else "-"
    )

    # =========================
    # GRAFICOS
    # =========================

    col1,col2 = st.columns(2)

    fig1 = px.bar(
        df.groupby("MOTIVO")
        .size()
        .reset_index(name="TOTAL")
        .sort_values("TOTAL",ascending=False)
        .head(10),
        x="MOTIVO",
        y="TOTAL",
        color="TOTAL",
        title="Top Motivos"
    )

    col1.plotly_chart(
        fig1,
        use_container_width=True
    )

    fig2 = px.bar(
        df.groupby("AREA")
        .size()
        .reset_index(name="TOTAL"),
        x="AREA",
        y="TOTAL",
        color="TOTAL",
        title="Solicitudes por Área"
    )

    col2.plotly_chart(
        fig2,
        use_container_width=True
    )

    col3,col4 = st.columns(2)

    fig3 = px.bar(
        df.groupby("TIENDA")
        .size()
        .reset_index(name="TOTAL")
        .sort_values("TOTAL",ascending=False)
        .head(15),
        x="TIENDA",
        y="TOTAL",
        color="TOTAL",
        title="Top Tiendas"
    )

    col3.plotly_chart(
        fig3,
        use_container_width=True
    )

    fig4 = px.bar(
        df.groupby("SKU")
        .size()
        .reset_index(name="TOTAL")
        .sort_values("TOTAL",ascending=False)
        .head(15),
        x="SKU",
        y="TOTAL",
        color="TOTAL",
        title="Top SKU"
    )

    col4.plotly_chart(
        fig4,
        use_container_width=True
    )

    fechas = (
        df.groupby("FECHA")
        .size()
        .reset_index(name="TOTAL")
    )

    fig5 = px.line(
        fechas,
        x="FECHA",
        y="TOTAL",
        markers=True,
        title="Evolución Temporal"
    )

    st.plotly_chart(
        fig5,
        use_container_width=True
    )

    # =========================
    # DETALLE
    # =========================

    with st.expander(
        "📋 Ver detalle de registros",
        expanded=False
    ):

        st.dataframe(
            df,
            use_container_width=True,
            height=500
        )

    # =========================
    # DESCARGA
    # =========================

    buffer = BytesIO()

    with pd.ExcelWriter(
        buffer,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            index=False,
            sheet_name="Detalle"
        )

    buffer.seek(0)

    st.download_button(
        label="📥 Descargar Excel Filtrado",
        data=buffer,
        file_name="Dashboard_Operacional.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:

    st.info(
        "📤 Sube un Excel para comenzar"
    )
