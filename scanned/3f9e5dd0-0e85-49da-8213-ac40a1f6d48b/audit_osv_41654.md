# [M] Coturn: Pre-authentication heap memory disclosure in ACME redirect (`try_acme_redirect`)

## Summary
Severity: Medium
Advisory: CVE-2026-62959
Aliases: GHSA-m23x-5qf5-988g
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-31
Source: https://osv.dev/vulnerability/CVE-2026-62959
Type: osv

## Details
Coturn is a free open source implementation of TURN and STUN Server. From 4.5.2 through 4.14.0, when Coturn is started with --acme-redirect <URL> and exposes a plaintext-TCP listener, an unauthenticated remote client can send a single ordinary HTTP GET request and receive a 301 response whose Location header contains up to ~870 bytes of adjacent process heap memory. The leaked region is a recycled network receive buffer that is reused without being zeroed, so on a busy server it can contain data from other clients' requests (TURN credentials, OAuth tokens, relayed payloads). Root cause is a signed→unsigned conversion. This issue is fixed in version 4.15.0.

## References
- https://github.com/coturn/coturn/releases/tag/4.15.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62959.json
- https://github.com/coturn/coturn/security/advisories/GHSA-m23x-5qf5-988g
- https://nvd.nist.gov/vuln/detail/CVE-2026-62959
- https://github.com/coturn/coturn/commit/960835886692fa04cf63ddd970c3f330740c87f4
- https://github.com/coturn/coturn/pull/1965
