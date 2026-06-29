import argparse
import sys
from pathlib import Path

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


ALGORITHM_CHOICES = ("lcs", "smith-waterman", "levenshtein")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="plagio-dp")
    parser.add_argument("arquivo_a")
    parser.add_argument("arquivo_b")
    parser.add_argument("-a", "--algoritmo", choices=ALGORITHM_CHOICES, default="lcs")
    parser.add_argument("-m", "--modo", choices=("word", "line"), default="word")
    parser.add_argument("--manter-stopwords", action="store_true")
    parser.add_argument("--saida-html")
    return parser


def analyze_files(
    path_a: Path,
    path_b: Path,
    algorithm: str,
    mode: str,
    remove_stopwords: bool
) -> dict:
    text_a = path_a.read_text(encoding="utf-8")
    text_b = path_b.read_text(encoding="utf-8")
    tokens_a = preprocess_and_tokenize(text_a, mode=mode, remove_stopwords=remove_stopwords)
    tokens_b = preprocess_and_tokenize(text_b, mode=mode, remove_stopwords=remove_stopwords)
    if algorithm == "lcs":
        matrix = compute_lcs_matrix(tokens_a, tokens_b)
        matches = traceback_lcs_alignment(matrix, tokens_a, tokens_b)
        score = calculate_similarity_score(len(matches), len(tokens_a), len(tokens_b))
        distance = None
    elif algorithm == "smith-waterman":
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
        "text_a": text_a,
        "text_b": text_b,
        "tokens_a": tokens_a,
        "tokens_b": tokens_b,
        "matrix": matrix,
        "matches": matches,
        "score": score,
        "distance": distance,
        "html_a": html_a,
        "html_b": html_b
    }


def build_html_report(result: dict, algorithm: str) -> str:
    return "\n".join([
        "<!doctype html>",
        '<html lang="pt-BR">',
        "<head>",
        '<meta charset="utf-8">',
        "<title>Relatorio de Plagio</title>",
        "<style>",
        "body { font-family: Arial, sans-serif; margin: 32px; color: #172033; background: #f7f8fb; }",
        "main { max-width: 1180px; margin: 0 auto; }",
        ".summary { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 20px 0; }",
        ".box { background: #ffffff; border: 1px solid #d9dfeb; border-radius: 8px; padding: 14px; }",
        ".label { color: #5d6b82; font-size: 12px; text-transform: uppercase; }",
        ".value { font-size: 26px; font-weight: 700; margin-top: 8px; }",
        ".texts { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }",
        ".panel { background: #ffffff; border: 1px solid #d9dfeb; border-radius: 8px; padding: 18px; line-height: 1.7; white-space: pre-wrap; }",
        ".highlight { background: #ffe58f; border-bottom: 2px solid #d48806; border-radius: 4px; padding: 1px 3px; }",
        "</style>",
        "</head>",
        "<body>",
        "<main>",
        "<h1>Relatorio de Plagio</h1>",
        '<div class="summary">',
        f'<div class="box"><div class="label">Algoritmo</div><div class="value">{algorithm}</div></div>',
        f'<div class="box"><div class="label">Similaridade</div><div class="value">{result["score"]:.1%}</div></div>',
        f'<div class="box"><div class="label">Tokens A</div><div class="value">{len(result["tokens_a"])}</div></div>',
        f'<div class="box"><div class="label">Tokens B</div><div class="value">{len(result["tokens_b"])}</div></div>',
        "</div>",
        '<section class="texts">',
        f'<article class="panel">{result["html_a"]}</article>',
        f'<article class="panel">{result["html_b"]}</article>',
        "</section>",
        "</main>",
        "</body>",
        "</html>",
        ""
    ])


def format_output(result: dict, algorithm: str) -> str:
    rows = len(result["matrix"])
    columns = len(result["matrix"][0]) if result["matrix"] else 0
    lines = [
        f"Algoritmo: {algorithm}",
        f"Tokens A: {len(result['tokens_a'])}",
        f"Tokens B: {len(result['tokens_b'])}",
        f"Correspondencias: {len(result['matches'])}",
        f"Similaridade: {result['score']:.2%}",
        f"Matriz DP: {rows}x{columns}"
    ]
    if result["distance"] is not None:
        lines.append(f"Distancia de edicao: {result['distance']:.0f}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    path_a = Path(args.arquivo_a)
    path_b = Path(args.arquivo_b)
    if not path_a.is_file():
        parser.error(f"arquivo nao encontrado: {path_a}")
    if not path_b.is_file():
        parser.error(f"arquivo nao encontrado: {path_b}")
    result = analyze_files(
        path_a,
        path_b,
        args.algoritmo,
        args.modo,
        not args.manter_stopwords
    )
    if args.saida_html:
        Path(args.saida_html).write_text(build_html_report(result, args.algoritmo), encoding="utf-8")
    print(format_output(result, args.algoritmo))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
