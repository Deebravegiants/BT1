# [H] NietThijmen ShoppingCart: Command injection in the connect function

## Summary
Severity: High
Advisory: GHSA-ggmw-mjhv-75rm
CVE: CVE-2024-53412
CWE: CWE-77
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-15
Source: https://github.com/advisories/GHSA-ggmw-mjhv-75rm
Type: github-advisory

## Affected
- Go: `github.com/NietThijmen/ShoppingCart` — affected >=0

## Details
Command injection in the connect function in NietThijmen ShoppingCart 0.0.2 allows an attacker to execute arbitrary shell commands and achieve remote code execution via injection of malicious payloads into the Port field

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-53412
- https://github.com/NietThijmen/ShoppingCart/issues/1
- https://github.com/Buckdray/vulnerability-research/blob/main/CVE-2024-53412/README.md
- https://github.com/NietThijmen/ShoppingCart
- https://github.com/advisories/GHSA-ggmw-mjhv-75rm
