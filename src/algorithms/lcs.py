def compute_dp_matrix(
    tokens_a: list[tuple[str, int, int]], 
    tokens_b: list[tuple[str, int, int]],
    **kwargs
) -> list[list[float]]:
    n = len(tokens_a)
    m = len(tokens_b)
    
    dp = [[0.0] * (m + 1) for _ in range(n + 1)]
    
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if tokens_a[i - 1][0] == tokens_b[j - 1][0]:
                dp[i][j] = dp[i - 1][j - 1] + 1.0
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
                
    return dp

def traceback_alignment(
    dp_matrix: list[list[float]], 
    tokens_a: list[tuple[str, int, int]], 
    tokens_b: list[tuple[str, int, int]]
) -> list[tuple[int, int]]:
    i = len(tokens_a)
    j = len(tokens_b)
    
    alignment = []
    
    if not dp_matrix or len(dp_matrix) != i + 1 or any(len(row) != j + 1 for row in dp_matrix):
        return []
        
    while i > 0 and j > 0:
        if tokens_a[i - 1][0] == tokens_b[j - 1][0]:
            alignment.append((i - 1, j - 1))
            i -= 1
            j -= 1
        elif dp_matrix[i - 1][j] >= dp_matrix[i][j - 1]:
            i -= 1
        else:
            j -= 1
            
    alignment.reverse()
    return alignment
