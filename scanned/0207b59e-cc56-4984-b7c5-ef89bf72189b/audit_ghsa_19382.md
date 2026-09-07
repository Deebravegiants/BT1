# [M] golang.org/x/net vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-vvgc-356p-c3xw
CVE: CVE-2025-22872
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-04-16
Source: https://github.com/advisories/GHSA-vvgc-356p-c3xw
Type: github-advisory

## Affected
- Go: `golang.org/x/net` — affected >=0 <0.38.0

## Details
The tokenizer incorrectly interprets tags with unquoted attribute values that end with a solidus character (/) as self-closing. When directly using Tokenizer, this can result in such tags incorrectly being marked as self-closing, and when using the Parse functions, this can result in content following such tags as being placed in the wrong scope during DOM construction, but only when tags are in foreign content (e.g. <math>, <svg>, etc contexts).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-22872
- https://go.dev/cl/662715
- https://go.dev/issue/73070
- https://groups.google.com/g/golang-announce/c/ezSKR9vqbqA
- https://pkg.go.dev/vuln/GO-2025-3595
- https://security.netapp.com/advisory/ntap-20250516-0007
