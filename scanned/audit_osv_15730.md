# [H] CVE-2019-19244

## Summary
Severity: High
Advisory: CVE-2019-19244
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-25
Source: https://osv.dev/vulnerability/CVE-2019-19244
Type: osv

## Details
sqlite3Select in select.c in SQLite 3.30.1 allows a crash if a sub-select uses both DISTINCT and window functions, and also has certain ORDER BY usage.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://usn.ubuntu.com/4205-1/
- https://github.com/sqlite/sqlite/commit/e59c562b3f6894f84c715772c4b116d7b5c01348
- https://www.oracle.com/security-alerts/cpuapr2020.html
