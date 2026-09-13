# [H] Litestar X-Forwarded-For Header Spoofing Vulnerability Enables Rate Limit Evasion

## Summary
Severity: High
Advisory: GHSA-hm36-ffrh-c77c
CVE: CVE-2025-59152
CWE: CWE-807
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-10-06
Source: https://github.com/advisories/GHSA-hm36-ffrh-c77c
Type: github-advisory

## Affected
- PyPI: `litestar` — affected >=2.17.0 <2.18.0

## Details
While testing Litestar's RateLimitMiddleware, I discovered that rate limits can be completely bypassed by manipulating the X-Forwarded-For header. This renders IP-based rate limiting ineffective against determined attackers.

## The Problem

Litestar's RateLimitMiddleware uses `cache_key_from_request()` to generate cache keys for rate limiting. When an X-Forwarded-For header is present, the middleware trusts it unconditionally and uses its value as part of the client identifier.

Since clients can set arbitrary X-Forwarded-For values, each different spoofed IP creates a separate rate limit bucket. An attacker can rotate through different header values to avoid hitting any single bucket's limit.

Looking at the relevant code in `litestar/middleware/rate_limit.py` around [line 127](https://github.com/litestar-org/litestar/blob/26f20ac6c52de2b4bf81161f7560c8bb4af6f382/litestar/middleware/rate_limit.py#L127), there's no validation of proxy headers or configuration for trusted proxies.

## Reproduction Steps

Here's a minimal test case

```python
from litestar import Litestar, get
from litestar.middleware.rate_limit import RateLimitConfig
import uvicorn

@get("/api/data")
def get_data() -> dict:
    return {"message": "sensitive data"}

rate_config = RateLimitConfig(rate_limit=("minute", 2))

app = Litestar(
    route_handlers=[get_data],
    middleware=[rate_config.middleware]
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

Testing the bypass

```bash
# Normal requests get rate limited after 2 requests
curl http://localhost:8000/api/data  # 200 OK
curl http://localhost:8000/api/data  # 200 OK  
curl http://localhost:8000/api/data  # 429 Too Many Requests

# But spoofing X-Forwarded-For bypasses the limit entirely
curl -H "X-Forwarded-For: 192.168.1.100" http://localhost:8000/api/data  # 200 OK
curl -H "X-Forwarded-For: 192.168.1.101" http://localhost:8000/api/data  # 200 OK
curl -H "X-Forwarded-For: 192.168.1.102" http://localhost:8000/api/data  # 200 OK
```

## Security Impact

This vulnerability has several concerning implications:

Brute Force Protection Bypass: Authentication endpoints protected by rate limiting become vulnerable to credential stuffing attacks. An attacker can attempt thousands of login combinations from a single source.

API Abuse: Public APIs relying on rate limiting for abuse prevention can be scraped or hammered without restriction.

Resource Exhaustion: While not a traditional DoS, the ability to bypass rate limits means attackers can consume more server resources than intended.

The issue is particularly problematic because many developers deploy Litestar applications directly (not behind a proxy) during development or in containerized environments, making this attack vector accessible.

## Potential Solutions

After reviewing how other frameworks handle this:

- Default to socket IP only: Don't trust proxy headers unless explicitly configured
- Trusted proxy configuration: Add settings to specify which proxy IPs are allowed to set forwarded headers
- Header validation: Implement basic validation of forwarded IP formats

Django handles this through `SECURE_PROXY_SSL_HEADER` and trusted proxy lists. Express.js has similar trusted proxy configurations.

For immediate mitigation, applications can deploy behind a properly configured reverse proxy that strips/overwrites client-controllable headers before they reach Litestar.

## Environment Details

- Litestar version: 2.17.0
- Python: 3.11

This affects any Litestar application using RateLimitMiddleware with default settings, which likely includes most applications that implement rate limiting.

## References
- https://github.com/litestar-org/litestar/security/advisories/GHSA-hm36-ffrh-c77c
- https://nvd.nist.gov/vuln/detail/CVE-2025-59152
- https://github.com/litestar-org/litestar/commit/42a89e043e50b515f8548a93954fe143f63cf9fb
- https://github.com/litestar-org/litestar
- https://github.com/litestar-org/litestar/blob/26f20ac6c52de2b4bf81161f7560c8bb4af6f382/litestar/middleware/rate_limit.py#L127
