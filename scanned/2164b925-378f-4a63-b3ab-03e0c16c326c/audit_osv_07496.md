# [H] BIT-sqlite-2020-9327

## Summary
Severity: High
Advisory: BIT-sqlite-2020-9327
Aliases: CVE-2020-9327
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-sqlite-2020-9327
Type: osv

## Affected
- Bitnami: `sqlite` — affected >=3.31.1 <3.31.2

## Details
In SQLite 3.31.1, isAuxiliaryVtabOperator allows attackers to trigger a NULL pointer dereference and segmentation fault because of generated column optimizations.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://security.gentoo.org/glsa/202003-16
- https://security.netapp.com/advisory/ntap-20200313-0002/
- https://usn.ubuntu.com/4298-1/
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.oracle.com/security-alerts/cpujul2020.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://www.sqlite.org/cgi/src/info/4374860b29383380
- https://www.sqlite.org/cgi/src/info/9d0d4ab95dc0c56e
- https://www.sqlite.org/cgi/src/info/abc473fb8fb99900
- https://nvd.nist.gov/vuln/detail/CVE-2020-9327
