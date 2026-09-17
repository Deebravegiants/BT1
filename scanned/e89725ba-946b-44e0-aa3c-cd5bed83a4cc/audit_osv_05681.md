# [H] Miscompilation allows memory corruption via CONVNOP-wrapped array copy in cmd/compile

## Summary
Severity: High
Advisory: BIT-golang-2026-27144
Aliases: CVE-2026-27144, GO-2026-4867
Ecosystem: Bitnami
Published: 2026-04-18
Source: https://osv.dev/vulnerability/BIT-golang-2026-27144
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.26.0 <1.26.2

## Details
The compiler is meant to unwrap pointers which are the operands of a memory move; a no-op interface conversion prevented the compiler from making the correct determination about non-overlapping moves, potentially leading to memory corruption at runtime.

## References
- https://go.dev/cl/763764
- https://go.dev/issue/78371
- https://groups.google.com/g/golang-announce/c/0uYbvbPZRWU
- https://nvd.nist.gov/vuln/detail/CVE-2026-27144
- https://pkg.go.dev/vuln/GO-2026-4867
