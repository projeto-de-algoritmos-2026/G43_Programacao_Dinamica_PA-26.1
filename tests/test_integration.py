from src.algorithms.lcs import (
    compute_dp_matrix as compute_lcs_matrix,
    traceback_alignment as traceback_lcs_alignment
)
from src.algorithms.smith_waterman import (
    compute_dp_matrix as compute_sw_matrix,
    traceback_alignment as traceback_sw_alignment
)
from pathlib import Path
import subprocess
import sys

from src.preprocessor import preprocess_and_tokenize
from src.reporter import calculate_similarity_score, generate_highlighted_html


ROOT_DIR = Path(__file__).resolve().parents[1]


def test_calculate_similarity_score():
    assert calculate_similarity_score(3, 6, 4) == 0.5
    assert calculate_similarity_score(0, 0, 0) == 0.0


def test_generate_highlighted_html_escapes_and_closes_spans():
    text_a = "Alpha <beta> & gamma beta"
    text_b = "Zero beta & delta"
    tokens_a = preprocess_and_tokenize(text_a, mode="word", remove_stopwords=False)
    tokens_b = preprocess_and_tokenize(text_b, mode="word", remove_stopwords=False)
    html_a, html_b = generate_highlighted_html(
        text_a,
        text_b,
        tokens_a,
        tokens_b,
        [(1, 1), (3, 1), (3, 1), (99, 99)]
    )
    assert html_a == 'Alpha &lt;<span class="highlight">beta</span>&gt; &amp; gamma <span class="highlight">beta</span>'
    assert html_b == 'Zero <span class="highlight">beta</span> &amp; delta'
    assert html_a.count('<span class="highlight">') == html_a.count("</span>")
    assert html_b.count('<span class="highlight">') == html_b.count("</span>")


def test_lcs_pipeline_generates_highlighted_html():
    text_a = "O gato preto dorme no sofá."
    text_b = "Um gato branco dorme no tapete."
    tokens_a = preprocess_and_tokenize(text_a, mode="word", remove_stopwords=True)
    tokens_b = preprocess_and_tokenize(text_b, mode="word", remove_stopwords=True)
    matrix = compute_lcs_matrix(tokens_a, tokens_b)
    matches = traceback_lcs_alignment(matrix, tokens_a, tokens_b)
    html_a, html_b = generate_highlighted_html(text_a, text_b, tokens_a, tokens_b, matches)
    score = calculate_similarity_score(len(matches), len(tokens_a), len(tokens_b))
    assert matches == [(0, 0), (2, 2)]
    assert score == 0.5
    assert html_a == 'O <span class="highlight">gato</span> preto <span class="highlight">dorme</span> no sofá.'
    assert html_b == 'Um <span class="highlight">gato</span> branco <span class="highlight">dorme</span> no tapete.'


def test_smith_waterman_pipeline_generates_local_highlighted_html():
    text_a = "Introdução distante. trecho copiado exatamente aqui. Fechamento."
    text_b = "Outro início sem relação, mas trecho copiado exatamente aparece."
    tokens_a = preprocess_and_tokenize(text_a, mode="word", remove_stopwords=False)
    tokens_b = preprocess_and_tokenize(text_b, mode="word", remove_stopwords=False)
    matrix = compute_sw_matrix(tokens_a, tokens_b)
    matches = traceback_sw_alignment(matrix, tokens_a, tokens_b)
    html_a, html_b = generate_highlighted_html(text_a, text_b, tokens_a, tokens_b, matches)
    assert [tokens_a[i][0] for i, _ in matches] == ["trecho", "copiado", "exatamente"]
    assert [tokens_b[j][0] for _, j in matches] == ["trecho", "copiado", "exatamente"]
    assert '<span class="highlight">trecho</span> <span class="highlight">copiado</span> <span class="highlight">exatamente</span>' in html_a
    assert '<span class="highlight">trecho</span> <span class="highlight">copiado</span> <span class="highlight">exatamente</span>' in html_b


def test_cli_lcs_end_to_end_generates_stdout_and_html(tmp_path):
    file_a = tmp_path / "a.txt"
    file_b = tmp_path / "b.txt"
    html_file = tmp_path / "relatorio.html"
    file_a.write_text("gato preto dorme cedo", encoding="utf-8")
    file_b.write_text("gato branco dorme tarde", encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli",
            str(file_a),
            str(file_b),
            "--algoritmo",
            "lcs",
            "--manter-stopwords",
            "--saida-html",
            str(html_file)
        ],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "Algoritmo: lcs" in result.stdout
    assert "Correspondencias: 2" in result.stdout
    assert "Similaridade: 50.00%" in result.stdout
    assert '<span class="highlight">gato</span>' in html_file.read_text(encoding="utf-8")


def test_cli_levenshtein_reports_edit_distance(tmp_path):
    file_a = tmp_path / "a.txt"
    file_b = tmp_path / "b.txt"
    file_a.write_text("alpha beta gamma", encoding="utf-8")
    file_b.write_text("alpha delta gamma", encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli",
            str(file_a),
            str(file_b),
            "--algoritmo",
            "levenshtein",
            "--manter-stopwords"
        ],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "Distancia de edicao: 1" in result.stdout


def test_cli_rejects_invalid_algorithm(tmp_path):
    file_a = tmp_path / "a.txt"
    file_b = tmp_path / "b.txt"
    file_a.write_text("a", encoding="utf-8")
    file_b.write_text("b", encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli",
            str(file_a),
            str(file_b),
            "--algoritmo",
            "invalido"
        ],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True
    )
    assert result.returncode != 0
