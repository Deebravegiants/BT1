# [H] CVE-2019-19926

## Summary
Severity: High
Advisory: CVE-2019-19926
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-12-23
Source: https://osv.dev/vulnerability/CVE-2019-19926
Type: osv

## Details
multiSelect in select.c in SQLite 3.30.1 mishandles certain errors during parsing, as demonstrated by errors from sqlite3WindowRewrite() calls. NOTE: this vulnerability exists because of an incomplete fix for CVE-2019-19880.

## References
- https://usn.ubuntu.com/4298-1/
- https://usn.ubuntu.com/4298-2/
- http://lists.opensuse.org/opensuse-security-announce/2020-02/msg00010.html
- http://lists.opensuse.org/opensuse-security-announce/2020-02/msg00015.html
- http://lists.opensuse.org/opensuse-security-announce/2020-02/msg00025.html
- https://access.redhat.com/errata/RHSA-2020:0514
- https://security.netapp.com/advisory/ntap-20200114-0003/
- https://www.debian.org/security/2020/dsa-4638
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://github.com/sqlite/sqlite/commit/8428b3b437569338a9d1e10c4cd8154acbe33089
- https://www.oracle.com/security-alerts/cpuapr2020.html
