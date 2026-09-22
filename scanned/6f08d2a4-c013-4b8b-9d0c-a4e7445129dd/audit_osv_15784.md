# [M] CVE-2019-19645

## Summary
Severity: Medium
Advisory: CVE-2019-19645
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-12-09
Source: https://osv.dev/vulnerability/CVE-2019-19645
Type: osv

## Details
alter.c in SQLite through 3.30.1 allows attackers to trigger infinite recursion via certain types of self-referential views in conjunction with ALTER TABLE statements.

## References
- https://security.netapp.com/advisory/ntap-20191223-0001/
- https://usn.ubuntu.com/4394-1/
- https://www.tenable.com/security/tns-2021-14
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://github.com/sqlite/sqlite/commit/38096961c7cd109110ac21d3ed7dad7e0cb0ae06
- https://www.oracle.com/security-alerts/cpuapr2020.html
