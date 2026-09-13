# [M] BIT-sqlite-2020-13631

## Summary
Severity: Medium
Advisory: BIT-sqlite-2020-13631
Aliases: CVE-2020-13631
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-sqlite-2020-13631
Type: osv

## Affected
- Bitnami: `sqlite` — affected >=0 <3.32.0

## Details
SQLite before 3.32.0 allows a virtual table to be renamed to the name of one of its shadow tables, related to alter.c and build.c.

## References
- http://seclists.org/fulldisclosure/2020/Dec/32
- http://seclists.org/fulldisclosure/2020/Nov/19
- http://seclists.org/fulldisclosure/2020/Nov/20
- http://seclists.org/fulldisclosure/2020/Nov/22
- https://bugs.chromium.org/p/chromium/issues/detail?id=1080459
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://lists.apache.org/thread.html/rc713534b10f9daeee2e0990239fa407e2118e4aa9e88a7041177497c%40%3Cissues.guacamole.apache.org%3E
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/L7KXQWHIY2MQP4LNM6ODWJENMXYYQYBN/
- https://security.FreeBSD.org/advisories/FreeBSD-SA-20:22.sqlite.asc
- https://security.gentoo.org/glsa/202007-26
- https://security.netapp.com/advisory/ntap-20200608-0002/
- https://sqlite.org/src/info/eca0ba2cf4c0fdf7
- https://support.apple.com/kb/HT211843
- https://support.apple.com/kb/HT211844
- https://support.apple.com/kb/HT211850
- https://support.apple.com/kb/HT211931
- https://support.apple.com/kb/HT211935
- https://support.apple.com/kb/HT211952
- https://usn.ubuntu.com/4394-1/
- https://www.oracle.com/security-alerts/cpujul2020.html
