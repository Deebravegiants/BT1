# [H] golang.org/x/text/language Denial of service via crafted Accept-Language header

## Summary
Severity: High
Advisory: GHSA-69ch-w2m2-3vjp
CVE: CVE-2022-32149
CWE: CWE-772
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-10-14
Source: https://github.com/advisories/GHSA-69ch-w2m2-3vjp
Type: github-advisory

## Affected
- Go: `golang.org/x/text` — affected >=0 <0.3.8

## Details
The BCP 47 tag parser has quadratic time complexity due to inherent aspects of its design. Since the parser is, by design, exposed to untrusted user input, this can be leveraged to force a program to consume significant time parsing Accept-Language headers. The parser cannot be easily rewritten to fix this behavior for various reasons. Instead the solution implemented in this CL is to limit the total complexity of tags passed into ParseAcceptLanguage by limiting the number of dashes in the string to 1000. This should be more than enough for the majority of real world use cases, where the number of tags being sent is likely to be in the single digits.

### Specific Go Packages Affected
golang.org/x/text/language

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-32149
- https://github.com/golang/go/issues/56152
- https://github.com/golang/text/commit/434eadcdbc3b0256971992e8c70027278364c72c
- https://github.com/golang/text
- https://go.dev/cl/442235
- https://go.dev/issue/56152
- https://groups.google.com/g/golang-announce/c/-hjNw559_tE/m/KlGTfid5CAAJ
- https://pkg.go.dev/vuln/GO-2022-1059
- https://security.netapp.com/advisory/ntap-20230203-0006
