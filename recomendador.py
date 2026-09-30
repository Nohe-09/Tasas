# Lógica de recomendación (compartida por el notebook y la app de Streamlit)
import numpy as np
import pandas as pd

MIN_DESEMBOLSOS = 5    # desembolsos mínimos de una entidad en el municipio para considerarla disponible
MIN_ENTIDADES = 3      # entidades mínimas disponibles para ofrecer una recomendación en un municipio
UMBRAL_EMPATE = 0.05   # diferencia de probabilidad por debajo de la cual se avisa que hay opciones muy similares


def nivel_monto(monto, bordes):
    """Nivel de monto (bajo, medio, alto) con los mismos cortes usados para construir la etiqueta."""
    e1, e2 = bordes
    if monto <= e1:
        return "bajo"
    if monto <= e2:
        return "medio"
    return "alto"


def entidades_disponibles(presencia, municipio):
    p = presencia[(presencia["municipio"] == municipio) & (presencia["n"] >= MIN_DESEMBOLSOS)]
    return sorted(p["entidad"].unique())


def municipios_con_cobertura(presencia):
    p = presencia[presencia["n"] >= MIN_DESEMBOLSOS]
    conteo = p.groupby("municipio")["entidad"].nunique()
    return sorted(conteo[conteo >= MIN_ENTIDADES].index)


def _buscar(tabla, filtros, columna):
    m = tabla
    for k, v in filtros.items():
        m = m[m[k] == v]
    if len(m) == 0:
        return None, 0
    return float(m.iloc[0][columna]), int(m.iloc[0]["n"])


def recomendar(bundle, referencia, mediana, presencia, producto, plazo, tipo_tasa, municipio, monto):
    """Devuelve la entidad con mayor probabilidad entre las que operan en el municipio."""
    disponibles = entidades_disponibles(presencia, municipio)
    if len(disponibles) < MIN_ENTIDADES:
        return {"ok": False,
                "mensaje": "No hay datos suficientes en este municipio para hacer una recomendación."}

    pipe = bundle["pipeline"]
    ciudad_grupo = municipio if municipio in bundle["ciudades_principales"] else "otras"
    X = pd.DataFrame([{"producto": producto, "plazo": plazo, "tipo_tasa": tipo_tasa,
                       "ciudad_grupo": ciudad_grupo, "monto_promedio": float(monto)}])
    prob = pd.Series(pipe.predict_proba(X)[0], index=pipe.classes_)
    prob = prob[prob.index.isin(disponibles)]
    if len(prob) == 0:
        return {"ok": False, "mensaje": "Ninguna de las entidades del modelo opera en este municipio."}
    if prob.sum() <= 0:
        prob = pd.Series(1.0 / len(prob), index=prob.index)
    else:
        prob = prob / prob.sum()
    prob = prob.sort_values(ascending=False)

    entidad = prob.index[0]
    p1 = float(prob.iloc[0])
    p2 = float(prob.iloc[1]) if len(prob) > 1 else 0.0
    nivel = nivel_monto(monto, bundle["bordes_monto"])

    # Tasa promedio observada de la entidad en el segmento (con alternativa sin nivel de monto)
    base = {"entidad": entidad, "producto": producto, "plazo": plazo}
    tasa_ref, n_ref = _buscar(referencia, {**base, "nivel_monto": nivel}, "tasa_ref")
    if tasa_ref is None:
        tasa_ref, n_ref = _buscar(referencia, {**base, "nivel_monto": "todos"}, "tasa_ref")
    seg = {"producto": producto, "plazo": plazo}
    med, n_med = _buscar(mediana, {**seg, "nivel_monto": nivel}, "mediana")
    if med is None:
        med, n_med = _buscar(mediana, {**seg, "nivel_monto": "todos"}, "mediana")

    return {"ok": True, "entidad": entidad, "confianza": p1,
            "empate": (p1 - p2) < UMBRAL_EMPATE, "nivel_monto": nivel,
            "tasa_ref": tasa_ref, "n_ref": n_ref, "mediana": med,
            "n_disponibles": len(disponibles)}
