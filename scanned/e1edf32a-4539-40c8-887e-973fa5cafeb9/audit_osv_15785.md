# [C] CVE-2019-19646

## Summary
Severity: Critical
Advisory: CVE-2019-19646
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-12-09
Source: https://osv.dev/vulnerability/CVE-2019-19646
Type: osv

## Details
pragma.c in SQLite through 3.30.1 mishandles NOT NULL in an integrity_check PRAGMA command in certain cases of generated columns.

## References
- https://github.com/sqlite/sqlite/commit/926f796e8feec15f3836aa0a060ed906f8ae04d3
- https://security.netapp.com/advisory/ntap-20191223-0001/
- https://www.sqlite.org/
- https://www.tenable.com/security/tns-2021-14
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://github.com/sqlite/sqlite/commit/ebd70eedd5d6e6a890a670b5ee874a5eae86b4dd
- https://www.oracle.com/security-alerts/cpuapr2020.html
