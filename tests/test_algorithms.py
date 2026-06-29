import pytest
from src.preprocessor import preprocess_and_tokenize
from src.algorithms.lcs import (
    compute_dp_matrix as compute_lcs_matrix,
    traceback_alignment as traceback_lcs_alignment
)
from src.algorithms.smith_waterman import (
    compute_dp_matrix as compute_sw_matrix,
    traceback_alignment as traceback_sw_alignment
)

def test_lcs_empty_input():
    tokens_a = []
    tokens_b = [("gato", 0, 4)]
    
    matrix = compute_lcs_matrix(tokens_a, tokens_b)
    assert len(matrix) == 1
    assert len(matrix[0]) == 2
    assert matrix[0][0] == 0.0
    assert matrix[0][1] == 0.0
    
    alignment = traceback_lcs_alignment(matrix, tokens_a, tokens_b)
    assert alignment == []

def test_lcs_no_match():
    tokens_a = preprocess_and_tokenize("ab", mode="word", remove_stopwords=False)
    tokens_b = preprocess_and_tokenize("cd", mode="word", remove_stopwords=False)
    
    matrix = compute_lcs_matrix(tokens_a, tokens_b)
    assert matrix[1][1] == 0.0
    
    alignment = traceback_lcs_alignment(matrix, tokens_a, tokens_b)
    assert alignment == []

def test_lcs_exact_match():
    text = "o gato subiu no telhado"
    tokens_a = preprocess_and_tokenize(text, mode="word", remove_stopwords=False)
    tokens_b = preprocess_and_tokenize(text, mode="word", remove_stopwords=False)
    
    matrix = compute_lcs_matrix(tokens_a, tokens_b)
    assert matrix[len(tokens_a)][len(tokens_b)] == len(tokens_a)
    
    alignment = traceback_lcs_alignment(matrix, tokens_a, tokens_b)
    expected = [(i, i) for i in range(len(tokens_a))]
    assert alignment == expected

def test_lcs_partial_match():
    text_a = "o rápido cão marrom pula"
    text_b = "o cão marrom salta rápido"
    
    tokens_a = preprocess_and_tokenize(text_a, mode="word", remove_stopwords=False)
    tokens_b = preprocess_and_tokenize(text_b, mode="word", remove_stopwords=False)
    
    matrix = compute_lcs_matrix(tokens_a, tokens_b)
    alignment = traceback_lcs_alignment(matrix, tokens_a, tokens_b)
    
    expected = [
        (0, 0),
        (2, 1),
        (3, 2)
    ]
    assert alignment == expected

def test_sw_empty_input():
    tokens_a = []
    tokens_b = [("gato", 0, 4)]
    
    matrix = compute_sw_matrix(tokens_a, tokens_b)
    assert len(matrix) == 1
    assert len(matrix[0]) == 2
    assert matrix[0][0] == 0.0
    
    alignment = traceback_sw_alignment(matrix, tokens_a, tokens_b)
    assert alignment == []

def test_sw_no_match():
    tokens_a = preprocess_and_tokenize("ab", mode="word", remove_stopwords=False)
    tokens_b = preprocess_and_tokenize("cd", mode="word", remove_stopwords=False)
    
    matrix = compute_sw_matrix(tokens_a, tokens_b)
    assert matrix[1][1] == 0.0
    
    alignment = traceback_sw_alignment(matrix, tokens_a, tokens_b)
    assert alignment == []

def test_sw_exact_match():
    text = "o gato subiu no telhado"
    tokens_a = preprocess_and_tokenize(text, mode="word", remove_stopwords=False)
    tokens_b = preprocess_and_tokenize(text, mode="word", remove_stopwords=False)
    
    matrix = compute_sw_matrix(tokens_a, tokens_b)
    assert matrix[len(tokens_a)][len(tokens_b)] == len(tokens_a) * 2.0
    
    alignment = traceback_sw_alignment(matrix, tokens_a, tokens_b)
    expected = [(i, i) for i in range(len(tokens_a))]
    assert alignment == expected

def test_sw_local_alignment():
    text_a = "Este é um texto longo que contém um segredo especial no meio dele."
    text_b = "Outro documento totalmente diferente contendo um segredo especial bem aqui."
    
    tokens_a = preprocess_and_tokenize(text_a, mode="word", remove_stopwords=False)
    tokens_b = preprocess_and_tokenize(text_b, mode="word", remove_stopwords=False)
    
    matrix = compute_sw_matrix(tokens_a, tokens_b)
    alignment = traceback_sw_alignment(matrix, tokens_a, tokens_b)
    
    expected = [
        (7, 5),
        (8, 6),
        (9, 7)
    ]
    assert alignment == expected
