# [H] BIT-sqlite-2020-11655

## Summary
Severity: High
Advisory: BIT-sqlite-2020-11655
Aliases: CVE-2020-11655
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-sqlite-2020-11655
Type: osv

## Affected
- Bitnami: `sqlite` — affected >=0 <3.31.2

## Details
SQLite through 3.31.1 allows attackers to cause a denial of service (segmentation fault) via a malformed window-function query because the AggInfo object's initialization is mishandled.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://lists.debian.org/debian-lts-announce/2020/05/msg00006.html
- https://lists.debian.org/debian-lts-announce/2020/08/msg00037.html
- https://security.FreeBSD.org/advisories/FreeBSD-SA-20:22.sqlite.asc
- https://security.gentoo.org/glsa/202007-26
- https://security.netapp.com/advisory/ntap-20200416-0001/
- https://usn.ubuntu.com/4394-1/
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.oracle.com/security-alerts/cpujul2020.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://www.tenable.com/security/tns-2021-14
- https://www3.sqlite.org/cgi/src/info/4a302b42c7bf5e11
- https://www3.sqlite.org/cgi/src/tktview?name=af4556bb5c
- https://nvd.nist.gov/vuln/detail/CVE-2020-11655
