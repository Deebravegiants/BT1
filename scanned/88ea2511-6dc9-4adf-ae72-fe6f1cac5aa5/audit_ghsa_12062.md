# [C] openssl-encrypt: TOTP rate limiter is in-memory only — not shared across workers, lost on restart

## Summary
Severity: Critical
Advisory: GHSA-h45m-mgcp-q388
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-h45m-mgcp-q388
Type: github-advisory

## Affected
- PyPI: `openssl-encrypt` — affected >=0 <1.4.0

## Details
## Severity: HIGH

### Summary

The TOTP brute-force rate limiter in `openssl_encrypt_server/modules/pepper/totp.py` at **lines 47-98** uses an in-memory `defaultdict(list)` as a class variable.

### Affected Code

```python
class TOTPRateLimiter:
    def __init__(self, ...):
        self.attempts: Dict[str, List[datetime]] = defaultdict(list)
        self.lockouts: Dict[str, datetime] = {}

class TOTPService:
    _rate_limiter = TOTPRateLimiter()  # Class variable, in-memory only
```

### Impact

1. Rate limit state is **not shared** across multiple server instances/workers — an attacker can distribute attempts
2. All rate limit state is **lost on server restart** — allows immediate retry
3. In multi-worker deployments, each worker has independent rate limit state

### Recommended Fix

- Use Redis or the database for rate limit state storage
- Or use a shared-memory approach for multi-worker deployments
- At minimum, persist lockout state to survive restarts

### Fix

Fixed in commit `2749bc0` on branch `releases/1.4.x` — added abstract RateLimitBackend with InMemoryBackend and DatabaseBackend implementations; defaults to DatabaseBackend when DB available.

## References
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-h45m-mgcp-q388
- https://github.com/jahlives/openssl_encrypt/commit/2749bc0949b34a5921a35fb4a3f1856fc51916de
- https://github.com/jahlives/openssl_encrypt
