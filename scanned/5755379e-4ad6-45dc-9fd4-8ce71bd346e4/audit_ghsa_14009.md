# [M] Algernon engine and themes vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-g47h-fgcw-g4ph
CVE: CVE-2023-26131
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-05-31
Source: https://github.com/advisories/GHSA-g47h-fgcw-g4ph
Type: github-advisory

## Affected
- Go: `github.com/xyproto/algernon` — affected >=0

## Details
All versions of the package github.com/xyproto/algernon/engine; all versions of the package github.com/xyproto/algernon/themes are vulnerable to Cross-site Scripting (XSS) via the `themes.NoPage(filename, theme)` function due to improper user input sanitization. Exploiting this vulnerability is possible when a file/resource is not found.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-26131
- https://github.com/xyproto/algernon
- https://github.com/xyproto/algernon/blob/aab484608651852d02a8a93f40baf53ed93e639a/engine/handlers.go#L512
- https://github.com/xyproto/algernon/blob/aab484608651852d02a8a93f40baf53ed93e639a/engine/handlers.go#L514
- https://github.com/xyproto/algernon/blob/aab484608651852d02a8a93f40baf53ed93e639a/themes/html.go#L145
- https://security.snyk.io/vuln/SNYK-GOLANG-GITHUBCOMXYPROTOALGERNONENGINE-3312111
- https://security.snyk.io/vuln/SNYK-GOLANG-GITHUBCOMXYPROTOALGERNONTHEMES-3312112
