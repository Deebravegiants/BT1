# [M] Arbitrary inputs are included in errors without any escaping in net/textproto

## Summary
Severity: Medium
Advisory: BIT-golang-2026-42507
Aliases: CVE-2026-42507, GO-2026-5039
Ecosystem: Bitnami
Published: 2026-06-05
Source: https://osv.dev/vulnerability/BIT-golang-2026-42507
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.26.0-0 <1.26.4

## Details
When returning errors, functions in the net/textproto package would include its input as part of the error. This might allow an attacker to inject misleading content to errors that are printed or logged.

## References
- https://go.dev/cl/777060
- https://go.dev/issue/79346
- https://groups.google.com/g/golang-announce/c/tKs3rmcBcKw
- https://nvd.nist.gov/vuln/detail/CVE-2026-42507
- https://pkg.go.dev/vuln/GO-2026-5039
