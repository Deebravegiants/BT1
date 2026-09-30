# [H] Failure to strip relative path components in net/url

## Summary
Severity: High
Advisory: BIT-golang-2022-32190
Aliases: CVE-2022-32190, GO-2022-0988
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2022-32190
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.19.0-0 <1.19.1

## Details
JoinPath and URL.JoinPath do not remove ../ path elements appended to a relative path. For example, JoinPath("https://go.dev", "../go") returns the URL "https://go.dev/../go", despite the JoinPath documentation stating that ../ path elements are removed from the result.

## References
- https://go.dev/cl/423514
- https://go.dev/issue/54385
- https://groups.google.com/g/golang-announce/c/x49AQzIVX-s
- https://pkg.go.dev/vuln/GO-2022-0988
- https://nvd.nist.gov/vuln/detail/CVE-2022-32190
