# [C] BIT-sqlite-2020-11656

## Summary
Severity: Critical
Advisory: BIT-sqlite-2020-11656
Aliases: CVE-2020-11656
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-sqlite-2020-11656
Type: osv

## Affected
- Bitnami: `sqlite` — affected >=0 <3.31.2

## Details
In SQLite through 3.31.1, the ALTER TABLE implementation has a use-after-free, as demonstrated by an ORDER BY clause that belongs to a compound SELECT statement.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://security.FreeBSD.org/advisories/FreeBSD-SA-20:22.sqlite.asc
- https://security.gentoo.org/glsa/202007-26
- https://security.netapp.com/advisory/ntap-20200416-0001/
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.oracle.com/security-alerts/cpujul2020.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://www.sqlite.org/src/info/d09f8c3621d5f7f8
- https://www.tenable.com/security/tns-2021-14
- https://www3.sqlite.org/cgi/src/info/b64674919f673602
- https://nvd.nist.gov/vuln/detail/CVE-2020-11656
