# [H] BIT-golang-2021-41772

## Summary
Severity: High
Advisory: BIT-golang-2021-41772
Aliases: CVE-2021-41772, GO-2021-0264
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2021-41772
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.17.0 <1.17.3

## Details
Go before 1.16.10 and 1.17.x before 1.17.3 allows an archive/zip Reader.Open panic via a crafted ZIP archive containing an invalid name or an empty filename field.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-744259.pdf
- https://groups.google.com/g/golang-announce/c/0fM21h43arc
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4OFS3M3OFB24SWPTIAPARKGPUMQVUY6Z/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ON7BQRRJZBOR5TJHURBAB3WLF4YXFC6Z/
- https://security.gentoo.org/glsa/202208-02
- https://security.netapp.com/advisory/ntap-20211210-0003/
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://nvd.nist.gov/vuln/detail/CVE-2021-41772
