# [C] BIT-golang-2022-23806

## Summary
Severity: Critical
Advisory: BIT-golang-2022-23806
Aliases: CVE-2022-23806, GO-2021-0319
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2022-23806
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.17.0 <1.17.7

## Details
Curve.IsOnCurve in crypto/elliptic in Go before 1.16.14 and 1.17.x before 1.17.7 can incorrectly return true in situations with a big.Int value that is not a valid field element.

## References
- https://groups.google.com/g/golang-announce/c/SUsQn0aSgPQ
- https://lists.debian.org/debian-lts-announce/2022/04/msg00017.html
- https://lists.debian.org/debian-lts-announce/2022/04/msg00018.html
- https://lists.debian.org/debian-lts-announce/2023/04/msg00021.html
- https://security.gentoo.org/glsa/202208-02
- https://security.netapp.com/advisory/ntap-20220225-0006/
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://nvd.nist.gov/vuln/detail/CVE-2022-23806
