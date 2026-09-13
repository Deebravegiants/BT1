# [M] BIT-golang-2021-33197

## Summary
Severity: Medium
Advisory: BIT-golang-2021-33197
Aliases: CVE-2021-33197, GO-2021-0241
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2021-33197
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.16.0 <1.16.5

## Details
In Go before 1.15.13 and 1.16.x before 1.16.5, some configurations of ReverseProxy (from net/http/httputil) result in a situation where an attacker is able to drop arbitrary headers.

## References
- https://groups.google.com/g/golang-announce
- https://groups.google.com/g/golang-announce/c/RgCMkAEQjSI
- https://security.gentoo.org/glsa/202208-02
- https://nvd.nist.gov/vuln/detail/CVE-2021-33197
