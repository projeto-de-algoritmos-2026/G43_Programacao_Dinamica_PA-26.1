import argparse
import csv
import statistics
import sys
from pathlib import Path
from time import perf_counter


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.algorithms.edit_distance import compute_dp_matrix as compute_edit_matrix
from src.algorithms.lcs import (
    compute_dp_matrix as compute_lcs_matrix,
    traceback_alignment as traceback_lcs_alignment
)
from src.algorithms.smith_waterman import (
    compute_dp_matrix as compute_sw_matrix,
    traceback_alignment as traceback_sw_alignment
)


ALGORITHMS = {
    "LCS": (compute_lcs_matrix, traceback_lcs_alignment),
    "Smith-Waterman": (compute_sw_matrix, traceback_sw_alignment),
    "Levenshtein": (compute_edit_matrix, None)
}


def make_tokens(size: int, offset: int) -> list[tuple[str, int, int]]:
    tokens = []
    cursor = 0
    for index in range(size):
        value = f"termo{(index + offset) % 31}"
        start = cursor
        end = start + len(value)
        tokens.append((value, start, end))
        cursor = end + 1
    return tokens


def measure(size: int, repeats: int) -> list[dict]:
    tokens_a = make_tokens(size, 0)
    tokens_b = make_tokens(size, size // 4)
    rows = []
    for name, functions in ALGORITHMS.items():
        compute, traceback = functions
        samples = []
        for _ in range(repeats):
            start = perf_counter()
            matrix = compute(tokens_a, tokens_b)
            if traceback:
                traceback(matrix, tokens_a, tokens_b)
            samples.append((perf_counter() - start) * 1000)
        rows.append({
            "algoritmo": name,
            "tokens": size,
            "tempo_ms": round(statistics.mean(samples), 4)
        })
    return rows


def write_csv(rows: list[dict], path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["algoritmo", "tokens", "tempo_ms"])
        writer.writeheader()
        writer.writerows(rows)


def make_svg(rows: list[dict]) -> str:
    width = 920
    height = 480
    left = 76
    right = 28
    top = 32
    bottom = 66
    plot_width = width - left - right
    plot_height = height - top - bottom
    sizes = sorted({row["tokens"] for row in rows})
    max_time = max(row["tempo_ms"] for row in rows) or 1.0
    min_size = min(sizes)
    max_size = max(sizes)
    colors = {
        "LCS": "#2563eb",
        "Smith-Waterman": "#d97706",
        "Levenshtein": "#059669"
    }
    def x_pos(size: int) -> float:
        if max_size == min_size:
            return left + plot_width / 2
        return left + (size - min_size) / (max_size - min_size) * plot_width
    def y_pos(value: float) -> float:
        return top + plot_height - value / max_time * plot_height
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#f7f8fb"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_height}" stroke="#64748b" stroke-width="1"/>',
        f'<line x1="{left}" y1="{top + plot_height}" x2="{left + plot_width}" y2="{top + plot_height}" stroke="#64748b" stroke-width="1"/>',
        f'<text x="{width / 2}" y="24" text-anchor="middle" font-family="Arial" font-size="18" font-weight="700" fill="#172033">Tempo medio por tamanho de entrada</text>',
        f'<text x="{width / 2}" y="{height - 16}" text-anchor="middle" font-family="Arial" font-size="13" fill="#334155">Tokens por texto</text>',
        f'<text x="18" y="{height / 2}" transform="rotate(-90 18 {height / 2})" text-anchor="middle" font-family="Arial" font-size="13" fill="#334155">Tempo medio (ms)</text>'
    ]
    for index in range(5):
        value = max_time * index / 4
        y = y_pos(value)
        lines.append(f'<line x1="{left}" y1="{y:.2f}" x2="{left + plot_width}" y2="{y:.2f}" stroke="#d9dfeb" stroke-width="1"/>')
        lines.append(f'<text x="{left - 10}" y="{y + 4:.2f}" text-anchor="end" font-family="Arial" font-size="12" fill="#475569">{value:.2f}</text>')
    for size in sizes:
        x = x_pos(size)
        lines.append(f'<text x="{x:.2f}" y="{top + plot_height + 22}" text-anchor="middle" font-family="Arial" font-size="12" fill="#475569">{size}</text>')
    for name, color in colors.items():
        points = []
        for row in rows:
            if row["algoritmo"] == name:
                points.append((x_pos(row["tokens"]), y_pos(row["tempo_ms"]), row["tempo_ms"]))
        point_text = " ".join(f"{x:.2f},{y:.2f}" for x, y, _ in points)
        lines.append(f'<polyline points="{point_text}" fill="none" stroke="{color}" stroke-width="3"/>')
        for x, y, value in points:
            lines.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4" fill="{color}"/>')
            lines.append(f'<title>{name}: {value:.4f} ms</title>')
    legend_x = left + plot_width - 176
    for index, (name, color) in enumerate(colors.items()):
        y = top + 22 + index * 24
        lines.append(f'<rect x="{legend_x}" y="{y - 10}" width="14" height="14" fill="{color}" rx="2"/>')
        lines.append(f'<text x="{legend_x + 22}" y="{y + 2}" font-family="Arial" font-size="13" fill="#172033">{name}</text>')
    lines.append("</svg>")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="docs")
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--sizes", nargs="+", type=int, default=[20, 40, 80, 120])
    args = parser.parse_args(argv)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for size in args.sizes:
        rows.extend(measure(size, args.repeats))
    write_csv(rows, output_dir / "benchmark_tempo.csv")
    (output_dir / "benchmark_tempo.svg").write_text(make_svg(rows), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
