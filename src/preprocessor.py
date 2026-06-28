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
    if not text:
        return []
        
    tokens = []
    
    if mode == "word":
        for match in re.finditer(r'\w+', text):
            word = match.group(0)
            start = match.start()
            end = match.end()
            
            sanitized = word.lower()
            
            if remove_stopwords and sanitized in PORTUGUESE_STOPWORDS:
                continue
                
            if sanitized:
                tokens.append((sanitized, start, end))
                
    elif mode == "line":
        for match in re.finditer(r'[^\r\n]+', text):
            line = match.group(0)
            start = match.start()
            end = match.end()
            
            cleaned = re.sub(r'[^\w\s]', '', line).lower()
            sanitized = " ".join(cleaned.split())
            
            if sanitized:
                tokens.append((sanitized, start, end))
                
    return tokens
