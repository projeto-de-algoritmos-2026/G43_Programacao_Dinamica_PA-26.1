import re

PORTUGUESE_STOPWORDS = {
    "o", "a", "os", "as", "um", "uma", "uns", "umas",
    "de", "do", "da", "dos", "das", "em", "no", "na", "nos", "nas",
    "para", "com", "por", "ao", "aos", "à", "às",
    "que", "se", "e", "ou", "mas", "porem", "contudo", "todavia",
    "este", "esta", "estes", "estas", "aquele", "aquela", "aqueles", "aquelas",
    "esse", "essa", "esses", "essas", "isto", "isso", "aquilo",
    "me", "te", "nos", "vos", "lhe", "lhes", "minha", "minhas", "nosso", "nossa",
    "nossos", "nossas", "seu", "sua", "seus", "suas", "como", "mais", "muito",
    "eu", "tu", "ele", "ela", "eles", "elas", "dele", "dela", "deles", "delas",
    "não", "sim", "desde", "entre", "sem", "sob", "sobre"
}

def preprocess_and_tokenize(
    text: str, 
    mode: str = "word", 
    remove_stopwords: bool = True
) -> list[tuple[str, int, int]]:
    """
    Limpa o texto bruto e quebra-o em uma lista de tokens sanitizados contendo metadados de posição.
    
    Argumentos:
        text (str): Texto de entrada original bruto.
        mode (str): "word" para tokenizar por palavra, "line" para tokenizar por linha.
        remove_stopwords (bool): Se True e mode for "word", filtra stopwords comuns.
        
    Retorna:
        list[tuple[str, int, int]]: Lista contendo tuplas no formato (token_higienizado, caractere_inicio, caractere_fim)
                                   representando as posições exatas dos caracteres no texto de entrada original bruto.
    """
    if not text:
        return []
        
    tokens = []
    
    if mode == "word":
        # Encontra todas as palavras usando expressão regular (\w+)
        # \w casa caracteres alfanuméricos Unicode (incluindo letras acentuadas do português)
        for match in re.finditer(r'\w+', text):
            word = match.group(0)
            start = match.start()
            end = match.end()
            
            # Sanitização: converte para minúsculas
            sanitized = word.lower()
            
            if remove_stopwords and sanitized in PORTUGUESE_STOPWORDS:
                continue
                
            if sanitized:
                tokens.append((sanitized, start, end))
                
    elif mode == "line":
        # Encontra linhas não vazias
        # Usando regex para encontrar linhas, mesmo que contenham apenas caracteres de espaço
        # Mas vamos sanitizá-las e pular se ficarem vazias
        for match in re.finditer(r'[^\r\n]+', text):
            line = match.group(0)
            start = match.start()
            end = match.end()
            
            # Sanitização:
            # 1. Remove pontuação (tudo que não é alfanumérico ou espaço)
            # 2. Converte para minúsculas
            # 3. Normaliza espaços múltiplos para um único espaço
            cleaned = re.sub(r'[^\w\s]', '', line).lower()
            sanitized = " ".join(cleaned.split())
            
            if sanitized:
                tokens.append((sanitized, start, end))
                
    return tokens
