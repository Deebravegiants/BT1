# [H] BIT-golang-2021-39293

## Summary
Severity: High
Advisory: BIT-golang-2021-39293
Aliases: CVE-2021-39293, GO-2022-0273
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2021-39293
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.17.0 <1.17.1

## Details
In archive/zip in Go before 1.16.8 and 1.17.x before 1.17.1, a crafted archive header (falsely designating that many files are present) can cause a NewReader or OpenReader panic. NOTE: this issue exists because of an incomplete fix for CVE-2021-33196.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-222547.pdf
- https://groups.google.com/g/golang-announce/c/dx9d7IOseHw
- https://lists.debian.org/debian-lts-announce/2023/04/msg00021.html
- https://security.netapp.com/advisory/ntap-20220217-0009/
- https://nvd.nist.gov/vuln/detail/CVE-2021-39293
