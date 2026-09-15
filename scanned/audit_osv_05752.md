# [H] Session takeover via Auth Proxy cache key collision

## Summary
Severity: High
Advisory: BIT-grafana-2026-14199
Aliases: CVE-2026-14199
Ecosystem: Bitnami
Published: 2026-09-08
Source: https://osv.dev/vulnerability/BIT-grafana-2026-14199
Type: osv

## Affected
- Bitnami: `grafana` — affected >=13.1.0 <13.2.1

## Details
Only self-managed Grafana instances with Auth Proxy authentication and identity caching enabled (sync_ttl greater than zero) are affected. The Auth Proxy cache key concatenated the username and forwarded identity attributes without a delimiter, so distinct identities could collide on one key. An authenticated user who shapes their own attributes to collide with a higher-privileged user's, while that user's cache entry is live, is authenticated as that user, up to Administrator (authentication bypass by spoofing).

## References
- https://grafana.com/security/security-advisories/cve-2026-14199
- https://nvd.nist.gov/vuln/detail/CVE-2026-14199
