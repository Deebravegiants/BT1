# [M] CVE-2019-19924

## Summary
Severity: Medium
Advisory: CVE-2019-19924
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2019-12-24
Source: https://osv.dev/vulnerability/CVE-2019-19924
Type: osv

## Details
SQLite 3.30.1 mishandles certain parser-tree rewriting, related to expr.c, vdbeaux.c, and window.c. This is caused by incorrect sqlite3WindowRewrite() error handling.

## References
- https://lists.apache.org/thread.html/r58af02e294bd07f487e2c64ffc0a29b837db5600e33b6e698b9d696b%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf4c02775860db415b4955778a131c2795223f61cb8c6a450893651e4%40%3Cissues.bookkeeper.apache.org%3E
- https://usn.ubuntu.com/4298-1/
- https://security.netapp.com/advisory/ntap-20200114-0003/
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://github.com/sqlite/sqlite/commit/8654186b0236d556aa85528c2573ee0b6ab71be3
- https://www.oracle.com/security-alerts/cpuapr2020.html
