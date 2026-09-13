# [H] CVE-2019-19959

## Summary
Severity: High
Advisory: CVE-2019-19959
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-01-03
Source: https://osv.dev/vulnerability/CVE-2019-19959
Type: osv

## Details
ext/misc/zipfile.c in SQLite 3.30.1 mishandles certain uses of INSERT INTO in situations involving embedded '\0' characters in filenames, leading to a memory-management error that can be detected by (for example) valgrind.

## References
- https://github.com/sqlite/sqlite/commit/1e490c4ca6b43a9cf8637d695907888349f69bec
- https://security.netapp.com/advisory/ntap-20200204-0001/
- https://usn.ubuntu.com/4298-1/
- https://www.oracle.com/security-alerts/cpuapr2020.html
- https://github.com/sqlite/sqlite/commit/d8f2d46cbc9925e034a68aaaf60aad788d9373c1
