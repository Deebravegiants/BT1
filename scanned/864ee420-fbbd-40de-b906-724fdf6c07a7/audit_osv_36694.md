# [M] Homarr affected by Unauthenticated SSRF / Port-Scan Primitive via widget.app.ping

## Summary
Severity: Medium
Advisory: CVE-2026-25123
Aliases: GHSA-c6rh-8wj4-gv74
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-02-06
Source: https://osv.dev/vulnerability/CVE-2026-25123
Type: osv

## Details
Homarr is an open-source dashboard. Prior to 1.52.0, a public (unauthenticated) tRPC endpoint widget.app.ping accepts an arbitrary url and performs a server-side request to that URL. This allows an unauthenticated attacker to trigger outbound HTTP requests from the Homarr server, enabling SSRF behavior and a reliable port-scanning primitive (open vs closed ports can be inferred from statusCode vs fetch failed and timing). This vulnerability is fixed in 1.52.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25123.json
- https://github.com/homarr-labs/homarr/security/advisories/GHSA-c6rh-8wj4-gv74
- https://nvd.nist.gov/vuln/detail/CVE-2026-25123
