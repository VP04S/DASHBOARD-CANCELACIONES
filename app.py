import streamlit as st
2
import pandas as pd
3
import plotly.express as px
4
from pathlib import Path
5
from io import BytesIO
6
 
7
# =========================
8
# CONFIG
9
# =========================
10
 
11
st.set_page_config(
12
page_title="Dashboard Operacional",
13
page_icon="📦",
14
layout="wide"
15
)
16
 
17
UPLOAD_PATH = Path("uploads")
18
UPLOAD_PATH.mkdir(exist_ok=True)
19
 
20
# =========================
21
# TITLE
22
# =========================
23
 
24
st.markdown("""
25
# 📦 Dashboard Operacional
26
### Seguimiento de Cancelaciones
27
""")
28
 
29
# =========================
30
# CARGA DE ARCHIVOS
31
# =========================
32
 
33
archivo = st.file_uploader(
34
"📤 Subir Excel",
35
type=["xlsx"]
36
)
37
 
38
if archivo is not None:
39
 
40
ruta = UPLOAD_PATH / archivo.name
41
 
42
with open(ruta, "wb") as f:
43
f.write(archivo.getbuffer())
44
 
45
st.success("✅ Archivo cargado correctamente")
46
 
47
# =========================
48
# LECTURA
49
# =========================
50
 
51
archivos = list(UPLOAD_PATH.glob("*.xlsx"))
52
 
53
if len(archivos) > 0:
54
 
55
dataframes = []
56
 
57
columnas = [
58
"MOTIVO",
59
"AREA",
60
"SKU",
61
"DESCRIPCION",
62
"TIENDA",
63
"TIPO",
64
"PCE",
65
"FECHA",
66
"REFERENCIA"
67
]
68
 
69
for file in archivos:
70
 
71
try:
72
 
73
df_temp = pd.read_excel(file)
74
 
75
df_temp.columns = (
76
df_temp.columns.astype(str)
77
.str.strip()
78
.str.upper()
79
)
80
 
81
faltantes = [
82
col
83
for col in columnas
84
if col not in df_temp.columns
85
]
86
 
87
if faltantes:
88
continue
89
 
90
df_temp = df_temp[columnas]
91
 
92
dataframes.append(df_temp)
93
 
94
except:
95
pass
96
 
97
if len(dataframes) == 0:
98
st.warning("No existen archivos válidos")
99
st.stop()
100
 
101
df = pd.concat(
102
dataframes,
103
ignore_index=True
104
)
105
 
106
df["FECHA"] = pd.to_datetime(
107
df["FECHA"],
108
errors="coerce"
109
)
110
 
111
# =========================
112
# SIDEBAR
113
# =========================
114
 
115
st.sidebar.title("🔎 Filtros")
116
 
117
fecha_min = df["FECHA"].min()
118
fecha_max = df["FECHA"].max()
119
 
120
if pd.notna(fecha_min):
121
 
122
rango_fecha = st.sidebar.date_input(
123
"FECHA",
124
value=(
125
fecha_min.date(),
126
fecha_max.date()
127
)
128
)
129
 
130
if len(rango_fecha) == 2:
131
 
132
inicio, fin = rango_fecha
133
 
134
df = df[
135
(df["FECHA"].dt.date >= inicio)
136
&
137
(df["FECHA"].dt.date <= fin)
138
]
139
 
140
motivo = st.sidebar.multiselect(
141
"MOTIVO",
142
sorted(df["MOTIVO"].dropna().unique())
143
)
144
 
145
area = st.sidebar.multiselect(
146
"AREA",
147
sorted(df["AREA"].dropna().unique())
148
)
149
 
150
sku = st.sidebar.multiselect(
151
"SKU",
152
sorted(df["SKU"].dropna().unique())
153
)
154
 
155
tienda = st.sidebar.multiselect(
156
"TIENDA",
157
sorted(df["TIENDA"].dropna().unique())
158
)
159
 
160
tipo = st.sidebar.multiselect(
161
"TIPO",
162
sorted(df["TIPO"].dropna().unique())
163
)
164
 
165
referencia = st.sidebar.multiselect(
166
"REFERENCIA",
167
sorted(df["REFERENCIA"].dropna().unique())
168
)
169
 
170
if motivo:
171
df = df[df["MOTIVO"].isin(motivo)]
172
 
173
if area:
174
df = df[df["AREA"].isin(area)]
175
 
176
if sku:
177
df = df[df["SKU"].isin(sku)]
178
 
179
if tienda:
180
df = df[df["TIENDA"].isin(tienda)]
181
 
182
if tipo:
183
df = df[df["TIPO"].isin(tipo)]
184
 
185
if referencia:
186
df = df[df["REFERENCIA"].isin(referencia)]
187
 
188
# =========================
189
# KPI
190
# =========================
191
 
192
c1,c2,c3,c4 = st.columns(4)
193
 
194
c1.metric(
195
"📦 Registros",
196
f"{len(df):,}"
197
)
198
 
199
c2.metric(
200
"📋 SKU",
201
f"{df['SKU'].nunique():,}"
202
)
203
 
204
c3.metric(
205
"🏪 Tiendas",
206
f"{df['TIENDA'].nunique():,}"
207
)
208
 
209
c4.metric(
210
"🏢 Áreas",
211
f"{df['AREA'].nunique():,}"
212
)
213
 
214
c5,c6,c7,c8 = st.columns(4)
215
 
216
c5.metric(
217
"📌 Motivos",
218
f"{df['MOTIVO'].nunique():,}"
219
)
220
 
221
c6.metric(
222
"💰 Total PCE",
223
f"{pd.to_numeric(df['PCE'], errors='coerce').sum():,.0f}"
224
)
225
 
226
c7.metric(
227
"🔍 Referencias",
228
f"{df['REFERENCIA'].nunique():,}"
229
)
230
 
231
c8.metric(
232
"📅 Última Fecha",
233
str(df["FECHA"].max().date())
234
if pd.notna(df["FECHA"].max())
235
else "-"
236
)
237
 
238
# =========================
239
# GRAFICOS
240
# =========================
241
 
242
col1,col2 = st.columns(2)
243
 
244
fig1 = px.bar(
245
df.groupby("MOTIVO")
246
.size()
247
.reset_index(name="TOTAL")
248
.sort_values("TOTAL",ascending=False)
249
.head(10),
250
x="MOTIVO",
251
y="TOTAL",
252
color="TOTAL",
253
title="Top Motivos"
254
)
255
 
256
col1.plotly_chart(
257
fig1,
258
use_container_width=True
259
)
260
 
261
fig2 = px.bar(
262
df.groupby("AREA")
263
.size()
264
.reset_index(name="TOTAL"),
265
x="AREA",
266
y="TOTAL",
267
color="TOTAL",
268
title="Solicitudes por Área"
269
)
270
 
271
col2.plotly_chart(
272
fig2,
273
use_container_width=True
274
)
275
 
276
col3,col4 = st.columns(2)
277
 
278
fig3 = px.bar(
279
df.groupby("TIENDA")
280
.size()
281
.reset_index(name="TOTAL")
282
.sort_values("TOTAL",ascending=False)
283
.head(15),
284
x="TIENDA",
285
y="TOTAL",
286
color="TOTAL",
287
title="Top Tiendas"
288
)
289
 
290
col3.plotly_chart(
291
fig3,
292
use_container_width=True
293
)
294
 
295
fig4 = px.bar(
296
df.groupby("SKU")
297
.size()
298
.reset_index(name="TOTAL")
299
.sort_values("TOTAL",ascending=False)
300
.head(15),
301
x="SKU",
302
y="TOTAL",
303
color="TOTAL",
304
title="Top SKU"
305
)
306
 
307
col4.plotly_chart(
308
fig4,
309
use_container_width=True
310
)
311
 
312
fechas = (
313
df.groupby("FECHA")
314
.size()
315
.reset_index(name="TOTAL")
316
)
317
 
318
fig5 = px.line(
319
fechas,
320
x="FECHA",
321
y="TOTAL",
322
markers=True,
323
title="Evolución Temporal"
324
)
325
 
326
st.plotly_chart(
327
fig5,
328
use_container_width=True
329
)
330
 
331
# =========================
332
# DETALLE
333
# =========================
334
 
335
with st.expander(
336
"📋 Ver detalle de registros",
337
expanded=False
338
):
339
 
340
st.dataframe(
341
df,
342
use_container_width=True,
343
height=500
344
)
345
 
346
# =========================
347
# DESCARGA
348
# =========================
349
 
350
buffer = BytesIO()
351
 
352
with pd.ExcelWriter(
353
buffer,
354
engine="openpyxl"
355
) as writer:
356
 
357
df.to_excel(
358
writer,
359
index=False,
360
sheet_name="Detalle"
361
)
362
 
363
buffer.seek(0)
364
 
365
st.download_button(
366
label="📥 Descargar Excel Filtrado",
367
data=buffer,
368
file_name="Dashboard_Operacional.xlsx",
369
mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
370
)
371
 
372
else:
373
 
374
st.info(
375
"📤 Sube un Excel para comenzar"
376
)
