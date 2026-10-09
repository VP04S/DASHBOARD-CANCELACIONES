import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Dashboard Cancelaciones",
    layout="wide"
)

UPLOAD_PATH = Path("uploads")
UPLOAD_PATH.mkdir(exist_ok=True)

st.title("📦 Dashboard de Cancelaciones")

archivo = st.file_uploader(
    "Subir Excel",
    type=["xlsx"]
)

if archivo is not None:

    ruta = UPLOAD_PATH / archivo.name

    with open(ruta, "wb") as f:
        f.write(archivo.getbuffer())

    st.success("Archivo cargado correctamente")

archivos = list(UPLOAD_PATH.glob("*.xlsx"))

if len(archivos) > 0:

    dataframes = []

    for file in archivos:

        df_temp = pd.read_excel(file)

        columnas = [
            "SKU",
            "TEINDA",
            "TIPO",
            "PCE",
            "SOLICITANTE",
            "MOTIVO",
            "FECHA SOLICITADA"
        ]

        df_temp = df_temp[columnas]

        dataframes.append(df_temp)

    df = pd.concat(dataframes, ignore_index=True)

    df["FECHA SOLICITADA"] = pd.to_datetime(
        df["FECHA SOLICITADA"],
        errors="coerce"
    )

    # ==========================
    # SIDEBAR FILTROS
    # ==========================

    st.sidebar.header("Filtros")

    fecha_min = df["FECHA SOLICITADA"].min()
    fecha_max = df["FECHA SOLICITADA"].max()

    if pd.notna(fecha_min) and pd.notna(fecha_max):

        rango_fecha = st.sidebar.date_input(
            "FECHA SOLICITADA",
            value=(fecha_min.date(), fecha_max.date())
        )

        if len(rango_fecha) == 2:

            fecha_inicio, fecha_fin = rango_fecha

            df = df[
                (df["FECHA SOLICITADA"].dt.date >= fecha_inicio)
                &
                (df["FECHA SOLICITADA"].dt.date <= fecha_fin)
            ]

    tipo = st.sidebar.multiselect(
        "TIPO",
        sorted(df["TIPO"].dropna().unique())
    )

    motivo = st.sidebar.multiselect(
        "MOTIVO",
        sorted(df["MOTIVO"].dropna().unique())
    )

    tienda = st.sidebar.multiselect(
        "TIENDA",
        sorted(df["TEINDA"].dropna().unique())
    )

    if tipo:
        df = df[df["TIPO"].isin(tipo)]

    if motivo:
        df = df[df["MOTIVO"].isin(motivo)]

    if tienda:
        df = df[df["TEINDA"].isin(tienda)]

    # ==========================
    # KPI'S
    # ==========================

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Total Solicitudes",
        len(df)
    )

    c2.metric(
        "SKU Únicos",
        df["SKU"].nunique()
    )

    c3.metric(
        "Tiendas",
        df["TEINDA"].nunique()
    )

    c4.metric(
        "Motivos",
        df["MOTIVO"].nunique()
    )

    # ==========================
    # GRAFICOS
    # ==========================

    col1, col2 = st.columns(2)

    motivo_df = (
        df.groupby("MOTIVO")
        .size()
        .reset_index(name="TOTAL")
    )

    graf1 = px.bar(
        motivo_df,
        x="MOTIVO",
        y="TOTAL",
        title="Solicitudes por Motivo"
    )

    col1.plotly_chart(
        graf1,
        use_container_width=True
    )

    tipo_df = (
        df.groupby("TIPO")
        .size()
        .reset_index(name="TOTAL")
    )

    graf2 = px.bar(
        tipo_df,
        x="TIPO",
        y="TOTAL",
        title="Solicitudes por Tipo"
    )

    col2.plotly_chart(
        graf2,
        use_container_width=True
    )

    fechas = (
        df.groupby("FECHA SOLICITADA")
        .size()
        .reset_index(name="TOTAL")
    )

    graf3 = px.line(
        fechas,
        x="FECHA SOLICITADA",
        y="TOTAL",
        title="Evolución de Solicitudes"
    )

    st.plotly_chart(
        graf3,
        use_container_width=True
    )

    topsku = (
        df.groupby("SKU")
        .size()
        .reset_index(name="TOTAL")
        .sort_values(
            "TOTAL",
            ascending=False
        )
        .head(10)
    )

    graf4 = px.bar(
        topsku,
        x="SKU",
        y="TOTAL",
        title
