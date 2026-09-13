# [H] CVE-2025-57632

## Summary
Severity: High
Advisory: CVE-2025-57632
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-25
Source: https://osv.dev/vulnerability/CVE-2025-57632
Type: osv

## Details
libsmb2 6.2+ is vulnerable to Buffer Overflow. When processing SMB2 chained PDUs (NextCommand), libsmb2 repeatedly calls smb2_add_iovector() to append to a fixed-size iovec array without checking the upper bound of v->niov (SMB2_MAX_VECTORS=256). An attacker can craft responses with many chained PDUs to overflow v->niov and perform heap out-of-bounds writes, causing memory corruption, crashes, and potentially arbitrary code execution. The SMB2_OPLOCK_BREAK path bypasses message ID validation.

## References
- https://gist.github.com/ZjW1nd/0b95b63307ceee7890e88e4abc6f041e
- https://github.com/sahlberg/libsmb2/blob/master/lib/compat.c#L569
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/57xxx/CVE-2025-57632.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-57632
- https://github.com/sahlberg/libsmb2/commit/5e75eebf922b338cdb548d60cffb3b997d2a12e8
- https://github.com/sahlberg/libsmb2
