def compute_dp_matrix(
    tokens_a: list[tuple[str, int, int]], 
    tokens_b: list[tuple[str, int, int]],
    **kwargs
) -> list[list[float]]:
    n = len(tokens_a)
    m = len(tokens_b)
    
    dp = [[0.0] * (m + 1) for _ in range(n + 1)]
    
    for i in range(n + 1):
        dp[i][0] = float(i)
    for j in range(m + 1):
        dp[0][j] = float(j)
        
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if tokens_a[i - 1][0] == tokens_b[j - 1][0]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1.0 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
                
    return dp
