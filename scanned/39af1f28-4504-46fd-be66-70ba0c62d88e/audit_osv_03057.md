# [M] ALPINE-CVE-2024-34702

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-34702
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-07-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-34702
Type: osv

## Affected
- Alpine:v3.17: `botan` — affected >=0 <2.19.5-r0
- Alpine:v3.18: `botan` — affected >=0 <2.19.5-r0
- Alpine:v3.19: `botan` — affected >=0 <2.19.5-r0
- Alpine:v3.20: `botan` — affected >=0 <2.19.5-r0
- Alpine:v3.21: `botan` — affected >=0 <2.19.5-r0
- Alpine:v3.21: `botan3` — affected >=0 <3.5.0-r0
- Alpine:v3.22: `botan3` — affected >=0 <3.5.0-r0
- Alpine:v3.23: `botan3` — affected >=0 <3.5.0-r0
- Alpine:v3.24: `botan3` — affected >=0 <3.5.0-r0

## Details
Botan is a C++ cryptography library. X.509 certificates can identify elliptic curves using either an object identifier or using explicit encoding of the parameters.  Prior to 3.5.0 and 2.19.5, checking name constraints in X.509 certificates is quadratic in the number of names and name constraints. An attacker who presented a certificate chain which contained a very large number of names in the SubjectAlternativeName, signed by a CA certificate which contained a large number of name constraints, could cause a denial of service. The problem has been addressed in Botan 3.5.0 and a partial backport has also been applied and is included in Botan 2.19.5.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-34702
