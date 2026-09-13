# [H] BIT-golang-2022-28327

## Summary
Severity: High
Advisory: BIT-golang-2022-28327
Aliases: CVE-2022-28327, GO-2022-0435
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2022-28327
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.18.0 <1.18.1

## Details
The generic P-256 feature in crypto/elliptic in Go before 1.17.9 and 1.18.x before 1.18.1 allows a panic via long scalar input.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-744259.pdf
- https://groups.google.com/g/golang-announce
- https://groups.google.com/g/golang-announce/c/oecdBNLOml8
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/42TYZC4OAY54TO75FBEFAPV5G7O4D5TM/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/F3BMW5QGX53CMIJIZWKXFKBJX2C5GWTY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NY6GEAJMNKKMU5H46QO4D7D6A24KSPXE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RCRSABD6CUDIZULZPZL5BJ3ET3A2NEJP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RQXU752ALW53OJAF5MG3WMR5CCZVLWW6/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Z55VUVGO7E5PJFXIOVAY373NZRHBNCI5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZY2SLWOQR4ZURQ7UBRZ7JIX6H6F5JHJR/
- https://security.gentoo.org/glsa/202208-02
- https://security.netapp.com/advisory/ntap-20220915-0010/
- https://nvd.nist.gov/vuln/detail/CVE-2022-28327
