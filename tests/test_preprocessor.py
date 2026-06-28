import pytest
from src.preprocessor import preprocess_and_tokenize

def test_preprocess_empty_text():
    assert preprocess_and_tokenize("") == []
    assert preprocess_and_tokenize("    ") == []
    assert preprocess_and_tokenize("\n\n\r\n") == []

def test_preprocess_only_punctuation():
    assert preprocess_and_tokenize("!?,.:;---") == []
    assert preprocess_and_tokenize("!!!\n???", mode="line") == []

def test_preprocess_words_normalization_and_punctuation():
    text = "Olá, Mundo! Isso é um Teste."
    tokens = preprocess_and_tokenize(text, mode="word", remove_stopwords=False)
    
    expected = [
        ("olá", 0, 3),
        ("mundo", 5, 10),
        ("isso", 12, 16),
        ("é", 17, 18),
        ("um", 19, 21),
        ("teste", 22, 27)
    ]
    assert tokens == expected

def test_preprocess_remove_stopwords():
    text = "O gato de botas na floresta."
    tokens_with = preprocess_and_tokenize(text, mode="word", remove_stopwords=True)
    expected_with = [
        ("gato", 2, 6),
        ("botas", 10, 15),
        ("floresta", 19, 27)
    ]
    assert tokens_with == expected_with

    tokens_without = preprocess_and_tokenize(text, mode="word", remove_stopwords=False)
    expected_without = [
        ("o", 0, 1),
        ("gato", 2, 6),
        ("de", 7, 9),
        ("botas", 10, 15),
        ("na", 16, 18),
        ("floresta", 19, 27)
    ]
    assert tokens_without == expected_without

def test_preprocess_line_mode():
    text = "Olá, mundo!   \nComo   vai você?\n\nLinha de teste!!!"
    tokens = preprocess_and_tokenize(text, mode="line")
    
    expected = [
        ("olá mundo", 0, 15),
        ("como vai você", 16, 33),
        ("linha de teste", 35, 52)
    ]
    assert tokens == expected
