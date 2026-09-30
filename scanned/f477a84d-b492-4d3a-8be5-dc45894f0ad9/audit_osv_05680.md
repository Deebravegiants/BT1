# [C] Missing bound checks can lead to memory corruption in safe Go in cmd/compile

## Summary
Severity: Critical
Advisory: BIT-golang-2026-27143
Aliases: CVE-2026-27143, GO-2026-4868
Ecosystem: Bitnami
Published: 2026-04-18
Source: https://osv.dev/vulnerability/BIT-golang-2026-27143
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.26.0 <1.26.2

## Details
Arithmetic over induction variables in loops were not correctly checked for underflow or overflow. As a result, the compiler would allow for invalid indexing to occur at runtime, potentially leading to memory corruption.

## References
- https://go.dev/cl/763765
- https://go.dev/issue/78333
- https://groups.google.com/g/golang-announce/c/0uYbvbPZRWU
- https://nvd.nist.gov/vuln/detail/CVE-2026-27143
- https://pkg.go.dev/vuln/GO-2026-4868
