# [C] LiteLLM: Authentication bypass via OIDC userinfo cache key collision

## Summary
Severity: Critical
Advisory: GHSA-jjhc-v7c2-5hh6
CVE: CVE-2026-35030
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-jjhc-v7c2-5hh6
Type: github-advisory

## Affected
- PyPI: `litellm` — affected >=0 <1.83.0

## Details
###  Impact

When JWT authentication is enabled (`enable_jwt_auth: true`), the OIDC userinfo cache uses `token[:20]` as the cache key. JWT headers produced by the same signing algorithm generate identical first 20 characters.

This configuration option is not enabled by default. **Most instances are not affected.**

An unauthenticated attacker can craft a token whose first 20 characters match a legitimate user's cached token. On cache hit, the attacker inherits the legitimate user's identity and permissions. This affects deployments with JWT/OIDC authentication enabled.

###  Patches

Fixed in v1.83.0. The cache key now uses the full hash of the JWT token.

###  Workarounds

Disable OIDC userinfo caching by setting the cache TTL to 0, or disable JWT authentication entirely.

## References
- https://github.com/BerriAI/litellm/security/advisories/GHSA-jjhc-v7c2-5hh6
- https://nvd.nist.gov/vuln/detail/CVE-2026-35030
- https://github.com/BerriAI/litellm
