from html import escape


def calculate_similarity_score(
    aligned_count: int,
    total_a: int,
    total_b: int
) -> float:
    denominator = max(total_a, total_b)
    if denominator <= 0:
        return 0.0
    return aligned_count / denominator


def generate_highlighted_html(
    original_text_a: str,
    original_text_b: str,
    tokens_a: list[tuple[str, int, int]],
    tokens_b: list[tuple[str, int, int]],
    matched_indices: list[tuple[int, int]]
) -> tuple[str, str]:
    ranges_a = _collect_ranges(original_text_a, tokens_a, [pair[0] for pair in matched_indices])
    ranges_b = _collect_ranges(original_text_b, tokens_b, [pair[1] for pair in matched_indices])
    return _highlight_text(original_text_a, ranges_a), _highlight_text(original_text_b, ranges_b)


def _collect_ranges(
    original_text: str,
    tokens: list[tuple[str, int, int]],
    indices: list[int]
) -> list[tuple[int, int]]:
    text_len = len(original_text)
    ranges = []
    for index in indices:
        if not isinstance(index, int):
            continue
        if index < 0 or index >= len(tokens):
            continue
        start = max(0, min(tokens[index][1], text_len))
        end = max(0, min(tokens[index][2], text_len))
        if start < end:
            ranges.append((start, end))
    return _merge_overlapping_ranges(ranges)


def _merge_overlapping_ranges(ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not ranges:
        return []
    ordered = sorted(set(ranges))
    merged = [ordered[0]]
    for start, end in ordered[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end:
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))
    return merged


def _highlight_text(original_text: str, ranges: list[tuple[int, int]]) -> str:
    parts = []
    cursor = 0
    for start, end in ranges:
        parts.append(escape(original_text[cursor:start]))
        parts.append(f'<span class="highlight">{escape(original_text[start:end])}</span>')
        cursor = end
    parts.append(escape(original_text[cursor:]))
    return "".join(parts)
