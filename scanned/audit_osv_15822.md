# [H] CVE-2019-19923

## Summary
Severity: High
Advisory: CVE-2019-19923
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-12-24
Source: https://osv.dev/vulnerability/CVE-2019-19923
Type: osv

## Details
flattenSubquery in select.c in SQLite 3.30.1 mishandles certain uses of SELECT DISTINCT involving a LEFT JOIN in which the right-hand side is a view. This can cause a NULL pointer dereference (or incorrect results).

## References
- https://usn.ubuntu.com/4298-1/
- http://lists.opensuse.org/opensuse-security-announce/2020-02/msg00010.html
- http://lists.opensuse.org/opensuse-security-announce/2020-02/msg00015.html
- http://lists.opensuse.org/opensuse-security-announce/2020-02/msg00025.html
- https://access.redhat.com/errata/RHSA-2020:0514
- https://security.netapp.com/advisory/ntap-20200114-0003/
- https://www.debian.org/security/2020/dsa-4638
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://github.com/sqlite/sqlite/commit/396afe6f6aa90a31303c183e11b2b2d4b7956b35
- https://www.oracle.com/security-alerts/cpuapr2020.html
