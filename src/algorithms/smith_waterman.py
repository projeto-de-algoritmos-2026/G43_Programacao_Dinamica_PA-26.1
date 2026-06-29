def compute_dp_matrix(
    tokens_a: list[tuple[str, int, int]], 
    tokens_b: list[tuple[str, int, int]],
    **kwargs
) -> list[list[float]]:
    w_match = float(kwargs.get("w_match", kwargs.get("match", 2.0)))
    w_mismatch = float(kwargs.get("w_mismatch", kwargs.get("mismatch", -1.0)))
    w_gap = float(kwargs.get("w_gap", kwargs.get("gap", -1.0)))
    
    n = len(tokens_a)
    m = len(tokens_b)
    
    dp = [[0.0] * (m + 1) for _ in range(n + 1)]
    
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if tokens_a[i - 1][0] == tokens_b[j - 1][0]:
                score_diag = dp[i - 1][j - 1] + w_match
            else:
                score_diag = dp[i - 1][j - 1] + w_mismatch
                
            score_up = dp[i - 1][j] + w_gap
            score_left = dp[i][j - 1] + w_gap
            
            dp[i][j] = max(0.0, score_diag, score_up, score_left)
            
    return dp

def traceback_alignment(
    dp_matrix: list[list[float]], 
    tokens_a: list[tuple[str, int, int]], 
    tokens_b: list[tuple[str, int, int]]
) -> list[tuple[int, int]]:
    i_len = len(tokens_a)
    j_len = len(tokens_b)
    
    if not dp_matrix or len(dp_matrix) != i_len + 1 or any(len(row) != j_len + 1 for row in dp_matrix):
        return []
        
    max_val = -1.0
    max_i, max_j = 0, 0
    for i in range(i_len + 1):
        for j in range(j_len + 1):
            if dp_matrix[i][j] > max_val:
                max_val = dp_matrix[i][j]
                max_i, max_j = i, j
                
    if max_val <= 0.0:
        return []
        
    w_match = 2.0
    w_mismatch = -1.0
    w_gap = -1.0
    
    i = max_i
    j = max_j
    alignment = []
    
    while i > 0 and j > 0 and dp_matrix[i][j] > 0.0:
        if tokens_a[i - 1][0] == tokens_b[j - 1][0]:
            if abs(dp_matrix[i][j] - (dp_matrix[i - 1][j - 1] + w_match)) < 1e-9:
                alignment.append((i - 1, j - 1))
                i -= 1
                j -= 1
                continue
        else:
            if abs(dp_matrix[i][j] - (dp_matrix[i - 1][j - 1] + w_mismatch)) < 1e-9:
                i -= 1
                j -= 1
                continue
                
        if abs(dp_matrix[i][j] - (dp_matrix[i - 1][j] + w_gap)) < 1e-9:
            i -= 1
        elif abs(dp_matrix[i][j] - (dp_matrix[i][j - 1] + w_gap)) < 1e-9:
            j -= 1
        else:
            v_diag = dp_matrix[i - 1][j - 1]
            v_up = dp_matrix[i - 1][j]
            v_left = dp_matrix[i][j - 1]
            
            if tokens_a[i - 1][0] == tokens_b[j - 1][0]:
                alignment.append((i - 1, j - 1))
                i -= 1
                j -= 1
            else:
                max_neighbor = max(v_diag, v_up, v_left)
                if max_neighbor == v_diag:
                    i -= 1
                    j -= 1
                elif max_neighbor == v_up:
                    i -= 1
                else:
                    j -= 1
                    
    alignment.reverse()
    return alignment
