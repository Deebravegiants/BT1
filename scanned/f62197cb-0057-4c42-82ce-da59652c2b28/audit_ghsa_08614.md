# [H] Hashicorp Boundary workers are vulnerable to a denial-of-service condition during node enrollment TLS handshakes

## Summary
Severity: High
Advisory: GHSA-7x9r-wcgg-w86f
CVE: CVE-2026-7776
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-7x9r-wcgg-w86f
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/boundary` — affected >=0 <0.19.5
- Go: `github.com/hashicorp/boundary` — affected >=0.20.0 <0.20.3
- Go: `github.com/hashicorp/boundary` — affected >=0.21.0 <0.21.3

## Details
Boundary Community Edition and Boundary Enterprise ("Boundary") workers are vulnerable to a denial-of-service condition during node enrollment TLS handshakes. An attacker with network access to the worker authentication listener may open a connection and delay or withhold the client certificate during the TLS handshake, causing worker connection handling to block. This may prevent legitimate worker connections from being accepted or routed. This vulnerability, CVE-2026-7776, is fixed in Boundary 0.21.3, 0.20.3, 0.19.5.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7776
- https://discuss.hashicorp.com/t/hcsec-2026-11-boundary-workers-vulnerable-to-denial-of-service-during-tls-handshake
- https://github.com/advisories/GHSA-7x9r-wcgg-w86f
- https://github.com/hashicorp/boundary
