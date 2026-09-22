# [M] 1Panel IP Access Control Bypass via Untrusted X-Forwarded-For Headers

## Summary
Severity: Medium
Advisory: GHSA-7cqv-qcq2-r765
CVE: CVE-2025-66508
CWE: CWE-290
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-12-08
Source: https://github.com/advisories/GHSA-7cqv-qcq2-r765
Type: github-advisory

## Affected
- Go: `github.com/1Panel-dev/1Panel` — affected >=0 <2.0.14
- Go: `github.com/1Panel-dev/1Panel/agent` — affected >=0 <0.0.0-20251201063338-94f7d78cc976

## Details
### Summary
The server trusts all reverse-proxy headers by default, so any remote client can spoof `X-Forwarded-For` to bypass IP-based protections (AllowIPs, API IP whitelist, “localhost-only” checks). All IP-based access control becomes ineffective.

### Details
- Gin is created with defaults (`gin.Default()`), which sets `TrustedProxies = 0.0.0.0/0` and uses `X-Forwarded-For`/`X-Real-IP` to compute `ClientIP()`.

- IP-based controls rely on `ClientIP()`:
    - AllowIPs / BindDomain (core/middleware/ip_limit.go, core/utils/security/security.go).
    - API IP whitelist (core/middleware/api_auth.go).
    - "localhost-only" checks that depend on `ClientIP()`.

- Because no trusted-proxy range is enforced, any client can send `X-Forwarded-For: 127.0.0.1` (or a whitelisted IP) and be treated as coming from that address.

### Impact
All IP-based access control is rendered ineffective: remote clients can masquerade as localhost or any whitelisted IP, defeating AllowIPs, API IP whitelists, and “localhost-only” protections.

## References
- https://github.com/1Panel-dev/1Panel/security/advisories/GHSA-7cqv-qcq2-r765
- https://nvd.nist.gov/vuln/detail/CVE-2025-66508
- https://github.com/1Panel-dev/1Panel/commit/94f7d78cc9768ee244da33e09408017d1f68b5ed
- https://github.com/1Panel-dev/1Panel
