import pandas as pd
import streamlit as st

from src.algorithms.edit_distance import compute_dp_matrix as compute_edit_matrix
from src.algorithms.lcs import (
    compute_dp_matrix as compute_lcs_matrix,
    traceback_alignment as traceback_lcs_alignment
)
from src.algorithms.smith_waterman import (
    compute_dp_matrix as compute_sw_matrix,
    traceback_alignment as traceback_sw_alignment
)
from src.preprocessor import preprocess_and_tokenize
from src.reporter import calculate_similarity_score, generate_highlighted_html


ALGORITHMS = {
    "LCS": "lcs",
    "Smith-Waterman": "smith_waterman",
    "Levenshtein": "levenshtein"
}


def run_analysis(
    text_a: str,
    text_b: str,
    algorithm: str,
    mode: str,
    remove_stopwords: bool
) -> dict:
    tokens_a = preprocess_and_tokenize(text_a, mode=mode, remove_stopwords=remove_stopwords)
    tokens_b = preprocess_and_tokenize(text_b, mode=mode, remove_stopwords=remove_stopwords)
    key = ALGORITHMS[algorithm]
    if key == "lcs":
        matrix = compute_lcs_matrix(tokens_a, tokens_b)
        matches = traceback_lcs_alignment(matrix, tokens_a, tokens_b)
        score = calculate_similarity_score(len(matches), len(tokens_a), len(tokens_b))
        distance = None
    elif key == "smith_waterman":
        matrix = compute_sw_matrix(tokens_a, tokens_b)
        matches = traceback_sw_alignment(matrix, tokens_a, tokens_b)
        score = calculate_similarity_score(len(matches), len(tokens_a), len(tokens_b))
        distance = None
    else:
        matrix = compute_edit_matrix(tokens_a, tokens_b)
        matches = []
        distance = matrix[-1][-1] if matrix and matrix[-1] else 0.0
        denominator = max(len(tokens_a), len(tokens_b))
        score = 1.0 - distance / denominator if denominator else 0.0
        score = max(0.0, min(1.0, score))
    html_a, html_b = generate_highlighted_html(text_a, text_b, tokens_a, tokens_b, matches)
    return {
        "tokens_a": tokens_a,
        "tokens_b": tokens_b,
        "matrix": matrix,
        "matches": matches,
        "score": score,
        "distance": distance,
        "html_a": html_a,
        "html_b": html_b
    }


def build_matrix_frame(
    matrix: list[list[float]],
    tokens_a: list[tuple[str, int, int]],
    tokens_b: list[tuple[str, int, int]]
) -> pd.DataFrame:
    rows = ["-"] + [token[0] for token in tokens_a]
    columns = ["-"] + [token[0] for token in tokens_b]
    return pd.DataFrame(matrix, index=rows, columns=columns)


def read_uploaded_file(uploaded_file) -> str:
    if uploaded_file is None:
        return ""
    return uploaded_file.getvalue().decode("utf-8", errors="replace")


def render_html_panel(title: str, body: str) -> None:
    st.markdown(
        f'<section class="result-panel">'
        f'<div class="panel-title">{title}</div>'
        f'<div class="highlight-body">{body}</div>'
        f'</section>',
        unsafe_allow_html=True
    )


def inject_styles() -> None:
    st.markdown(
        "<style>"
        ".stApp { background: #f7f8fb; color: #172033; }"
        ".main .block-container { max-width: 1220px; padding-top: 2rem; padding-bottom: 3rem; }"
        "h1, h2, h3 { letter-spacing: 0; }"
        ".metric-row { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin: 18px 0; }"
        ".metric-box { background: #ffffff; border: 1px solid #d9dfeb; border-radius: 8px; padding: 14px 16px; min-height: 86px; }"
        ".metric-label { color: #5d6b82; font-size: 0.78rem; text-transform: uppercase; margin-bottom: 8px; }"
        ".metric-value { color: #162032; font-size: 1.55rem; font-weight: 700; }"
        ".result-panel { background: #ffffff; border: 1px solid #d9dfeb; border-radius: 8px; min-height: 360px; padding: 18px; }"
        ".panel-title { color: #42526b; font-size: 0.82rem; font-weight: 700; text-transform: uppercase; margin-bottom: 14px; }"
        ".highlight-body { color: #18243a; font-size: 1rem; line-height: 1.75; white-space: pre-wrap; overflow-wrap: anywhere; }"
        ".highlight { background: #ffe58f; border-bottom: 2px solid #d48806; border-radius: 4px; padding: 1px 3px; }"
        "@media (max-width: 820px) { .metric-row { grid-template-columns: repeat(2, minmax(0, 1fr)); } }"
        "</style>",
        unsafe_allow_html=True
    )


def main() -> None:
    st.set_page_config(page_title="Detector de Plagio", page_icon="DP", layout="wide")
    inject_styles()
    st.title("Detector de Plagio")
    st.caption("Alinhamento de sequencias com programacao dinamica")
    with st.sidebar:
        st.header("Configuracao")
        algorithm = st.selectbox("Algoritmo", list(ALGORITHMS.keys()))
        mode = st.radio("Tokenizacao", ["word", "line"], horizontal=True)
        remove_stopwords = st.toggle("Remover stopwords", value=True)
        st.divider()
        uploaded_a = st.file_uploader("Arquivo A", type=["txt", "py", "md", "csv"])
        uploaded_b = st.file_uploader("Arquivo B", type=["txt", "py", "md", "csv"])
    default_a = read_uploaded_file(uploaded_a)
    default_b = read_uploaded_file(uploaded_b)
    col_a, col_b = st.columns(2)
    with col_a:
        text_a = st.text_area("Texto A", value=default_a, height=260)
    with col_b:
        text_b = st.text_area("Texto B", value=default_b, height=260)
    if not text_a and not text_b:
        st.info("Carregue arquivos ou cole textos para iniciar a analise.")
        return
    result = run_analysis(text_a, text_b, algorithm, mode, remove_stopwords)
    matrix = result["matrix"]
    matches = result["matches"]
    tokens_a = result["tokens_a"]
    tokens_b = result["tokens_b"]
    st.markdown(
        f'<div class="metric-row">'
        f'<div class="metric-box"><div class="metric-label">Similaridade</div><div class="metric-value">{result["score"]:.1%}</div></div>'
        f'<div class="metric-box"><div class="metric-label">Tokens A</div><div class="metric-value">{len(tokens_a)}</div></div>'
        f'<div class="metric-box"><div class="metric-label">Tokens B</div><div class="metric-value">{len(tokens_b)}</div></div>'
        f'<div class="metric-box"><div class="metric-label">Correspondencias</div><div class="metric-value">{len(matches)}</div></div>'
        f'</div>',
        unsafe_allow_html=True
    )
    if result["distance"] is not None:
        st.metric("Distancia de edicao", f"{result['distance']:.0f}")
    st.subheader("Highlights")
    result_col_a, result_col_b = st.columns(2)
    with result_col_a:
        render_html_panel("Texto A", result["html_a"])
    with result_col_b:
        render_html_panel("Texto B", result["html_b"])
    st.subheader("Matriz DP")
    if len(matrix) * len(matrix[0]) if matrix else 0:
        frame = build_matrix_frame(matrix, tokens_a, tokens_b)
        st.dataframe(frame, use_container_width=True, height=420)
    else:
        st.info("A matriz esta vazia para as entradas atuais.")


if __name__ == "__main__":
    main()
