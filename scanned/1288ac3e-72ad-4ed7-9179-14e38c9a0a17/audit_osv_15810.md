# [H] CVE-2019-19880

## Summary
Severity: High
Advisory: CVE-2019-19880
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-12-18
Source: https://osv.dev/vulnerability/CVE-2019-19880
Type: osv

## Details
exprListAppendList in window.c in SQLite 3.30.1 allows attackers to trigger an invalid pointer dereference because constant integer values in ORDER BY clauses of window definitions are mishandled.

## References
- https://usn.ubuntu.com/4298-1/
- http://lists.opensuse.org/opensuse-security-announce/2020-02/msg00010.html
- http://lists.opensuse.org/opensuse-security-announce/2020-02/msg00015.html
- http://lists.opensuse.org/opensuse-security-announce/2020-02/msg00025.html
- https://access.redhat.com/errata/RHSA-2020:0514
- https://security.netapp.com/advisory/ntap-20200114-0001/
- https://www.debian.org/security/2020/dsa-4638
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://github.com/sqlite/sqlite/commit/75e95e1fcd52d3ec8282edb75ac8cd0814095d54
- https://www.oracle.com/security-alerts/cpuapr2020.html
