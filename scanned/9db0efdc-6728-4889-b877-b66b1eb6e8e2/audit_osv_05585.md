# [H] BIT-golang-2021-41771

## Summary
Severity: High
Advisory: BIT-golang-2021-41771
Aliases: CVE-2021-41771, GO-2021-0263
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2021-41771
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.17.0 <1.17.3

## Details
ImportedSymbols in debug/macho (for Open or OpenFat) in Go before 1.16.10 and 1.17.x before 1.17.3 Accesses a Memory Location After the End of a Buffer, aka an out-of-bounds slice situation.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-744259.pdf
- https://groups.google.com/g/golang-announce/c/0fM21h43arc
- https://lists.debian.org/debian-lts-announce/2022/01/msg00016.html
- https://lists.debian.org/debian-lts-announce/2022/01/msg00017.html
- https://lists.debian.org/debian-lts-announce/2023/04/msg00021.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4OFS3M3OFB24SWPTIAPARKGPUMQVUY6Z/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ON7BQRRJZBOR5TJHURBAB3WLF4YXFC6Z/
- https://security.gentoo.org/glsa/202208-02
- https://security.netapp.com/advisory/ntap-20211210-0003/
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://nvd.nist.gov/vuln/detail/CVE-2021-41771
