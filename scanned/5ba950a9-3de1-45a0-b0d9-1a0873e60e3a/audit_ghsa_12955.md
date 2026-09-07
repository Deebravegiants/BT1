# [M] Improper rendering of text nodes in golang.org/x/net/html

## Summary
Severity: Medium
Advisory: GHSA-2wrh-6pvc-2jm9
CVE: CVE-2023-3978
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-08-02
Source: https://github.com/advisories/GHSA-2wrh-6pvc-2jm9
Type: github-advisory

## Affected
- Go: `golang.org/x/net` — affected >=0 <0.13.0

## Details
Text nodes not in the HTML namespace are incorrectly literally rendered, causing text which should be escaped to not be. This could lead to an XSS attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-3978
- https://go.dev/cl/514896
- https://go.dev/issue/61615
- https://pkg.go.dev/vuln/GO-2023-1988
