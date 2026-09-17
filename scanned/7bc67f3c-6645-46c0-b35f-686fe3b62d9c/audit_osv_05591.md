# [H] BIT-golang-2022-23773

## Summary
Severity: High
Advisory: BIT-golang-2022-23773
Aliases: CVE-2022-23773, GO-2022-0318
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2022-23773
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.17.0 <1.17.7

## Details
cmd/go in Go before 1.16.14 and 1.17.x before 1.17.7 can misinterpret branch names that falsely appear to be version tags. This can lead to incorrect access control if an actor is supposed to be able to create branches but not tags.

## References
- https://groups.google.com/g/golang-announce/c/SUsQn0aSgPQ
- https://security.gentoo.org/glsa/202208-02
- https://security.netapp.com/advisory/ntap-20220225-0006/
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://nvd.nist.gov/vuln/detail/CVE-2022-23773
