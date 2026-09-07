# [H] golang.org/x/text/language Out-of-bounds Read vulnerability

## Summary
Severity: High
Advisory: GHSA-ppp9-7jff-5vj2
CVE: CVE-2021-38561
CWE: CWE-125
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-12-26
Source: https://github.com/advisories/GHSA-ppp9-7jff-5vj2
Type: github-advisory

## Affected
- Go: `golang.org/x/text` — affected >=0 <0.3.7

## Details
golang.org/x/text/language in golang.org/x/text before 0.3.7 can panic with an out-of-bounds read during BCP 47 language tag parsing. Index calculation is mishandled. If parsing untrusted user input, this can be used as a vector for a denial-of-service attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-38561
- https://deps.dev/advisory/OSV/GO-2021-0113
- https://go.dev/cl/340830
- https://go.googlesource.com/text/+/383b2e75a7a4198c42f8f87833eefb772868a56f
- https://groups.google.com/g/golang-announce
- https://pkg.go.dev/golang.org/x/text/language
- https://pkg.go.dev/vuln/GO-2021-0113
