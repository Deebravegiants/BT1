# [H] Inefficient policy validation in crypto/x509

## Summary
Severity: High
Advisory: BIT-golang-2026-32281
Aliases: CVE-2026-32281, GO-2026-4946
Ecosystem: Bitnami
Published: 2026-04-13
Source: https://osv.dev/vulnerability/BIT-golang-2026-32281
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.26.0-0 <1.26.2

## Details
Validating certificate chains which use policies is unexpectedly inefficient when certificates in the chain contain a very large number of policy mappings, possibly causing denial of service. This only affects validation of otherwise trusted certificate chains, issued by a root CA in the VerifyOptions.Roots CertPool, or in the system certificate pool.

## References
- https://go.dev/cl/758061
- https://go.dev/issue/78281
- https://groups.google.com/g/golang-announce/c/0uYbvbPZRWU
- https://nvd.nist.gov/vuln/detail/CVE-2026-32281
- https://pkg.go.dev/vuln/GO-2026-4946
