# Recomendador de entidad financiera para crédito de vivienda

Aplicación en Streamlit que recomienda **una** entidad (banco comercial o compañía de financiamiento) con alta
probabilidad de ofrecer una tasa competitiva para un crédito de vivienda, según producto, plazo, tipo de tasa,
monto y ciudad.

## Datos
Datos Abiertos Colombia · Superintendencia Financiera de Colombia, *Tasas de interés activas por tipo de crédito*
(filtro vivienda, tipos de entidad 1 y 4, cortes semanales del 3 de julio al 11 de septiembre de 2026).
https://www.datos.gov.co/Econom-a-y-Finanzas/Tasas-de-inter-s-activas-por-tipo-de-cr-dito/w9zh-vetq/about_data

## Cómo funciona
1. Se define un registro como *competitivo* si su tasa está en el tercio más bajo de su segmento (producto, plazo y nivel de monto).
2. Un modelo de clasificación multiclase aprende qué entidad aparece entre los registros competitivos para cada perfil.
3. La aplicación calcula la probabilidad de cada entidad, deja solo las que tienen desembolsos en la ciudad elegida y muestra la de mayor probabilidad.

## Archivos
- `app.py`: interfaz de Streamlit. `recomendador.py`: lógica de la recomendación.
- `modelo_recomendador.joblib`: pipeline serializado (codificación + modelo).
- `referencia_tasas.csv`, `mediana_segmento.csv`, `presencia_entidad_municipio.csv`, `municipios.csv`, `tipos_tasa.csv`: tablas de apoyo.

## Ejecución local
```
pip install -r requirements.txt
streamlit run app.py
```

## Limitaciones
Es una guía de referencia basada en desembolsos ya realizados. No incluye el perfil crediticio del cliente, comisiones ni seguros,
y la tasa real se confirma con la entidad. Solo cubre las entidades con datos suficientes y las ciudades con al menos tres entidades presentes.

## Publicación en Streamlit Community Cloud
1. Sube al repositorio de GitHub **los archivos sueltos** (no el .zip) y deja `app.py` en la raíz del repositorio.
2. En share.streamlit.io elige el repositorio, la rama y `app.py` como archivo principal.
3. En *Advanced settings* elige **Python 3.12** (scikit-learn 1.8 requiere Python 3.11 o superior).
4. Si la aplicación no abre, entra a *Manage app* y revisa los registros. Las causas más comunes: falta algún archivo del repositorio, `requirements.txt` con una versión de scikit-learn distinta a la del entrenamiento, o una versión de Python incompatible.
