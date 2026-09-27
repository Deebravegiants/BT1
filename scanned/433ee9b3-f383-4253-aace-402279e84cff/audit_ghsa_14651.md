# [C] GoCast OS Command Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-5qww-56gc-f66c
CVE: CVE-2024-28892
CWE: CWE-78
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-12-20
Source: https://github.com/advisories/GHSA-5qww-56gc-f66c
Type: github-advisory

## Affected
- Go: `github.com/mayuresh82/gocast` — affected >=0

## Details
An OS command injection vulnerability exists in the name parameter of GoCast 1.1.3. A specially crafted HTTP request can lead to arbitrary command execution. An attacker can make an unauthenticated HTTP request to trigger this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-28892
- https://github.com/mayuresh82/gocast
- https://talosintelligence.com/vulnerability_reports/TALOS-2024-1960
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2024-1960
