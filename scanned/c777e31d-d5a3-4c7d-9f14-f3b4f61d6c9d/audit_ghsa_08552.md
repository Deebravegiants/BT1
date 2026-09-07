# [M] Grafana: SQL Expressions Read File From Disk

## Summary
Severity: Medium
Advisory: GHSA-gxcp-jjxh-rwp4
CVE: CVE-2026-33380
CWE: CWE-552
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-13
Source: https://github.com/advisories/GHSA-gxcp-jjxh-rwp4
Type: github-advisory

## Affected
- Go: `github.com/grafana/grafana` — affected >=0 <1.9.2-0.20260513165311-fb7336fc36c1

## Details
A vulnerability in SQL Expressions allows an authenticated attacker to read arbitrary files from the Grafana server's filesystem. Only instances with the sqlExpressions feature toggle enabled are vulnerable.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-33380
- https://github.com/grafana/grafana/commit/fb7336fc36c14e1ff869482c5085ddb9f39e1b86
- https://github.com/grafana/grafana
- https://grafana.com/security/security-advisories/cve-2026-33380
