# [H] BIT-libpython-2022-26488

## Summary
Severity: High
Advisory: BIT-libpython-2022-26488
Aliases: BIT-python-2022-26488, BIT-python-min-2022-26488, CVE-2022-26488
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libpython-2022-26488
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.9.0 <3.9.11

## Details
In Python before 3.10.3 on Windows, local users can gain privileges because the search path is inadequately secured. The installer may allow a local attacker to add user-writable directories to the system search path. To exploit, an administrator must have installed Python for all users and enabled PATH entries. A non-administrative user can trigger a repair that incorrectly adds user-writable paths into PATH, enabling search-path hijacking of other users and system services. This affects Python (CPython) through 3.7.12, 3.8.x through 3.8.12, 3.9.x through 3.9.10, and 3.10.x through 3.10.2.

## References
- https://mail.python.org/archives/list/security-announce%40python.org/thread/657Z4XULWZNIY5FRP3OWXHYKUSIH6DMN/
- https://nvd.nist.gov/vuln/detail/CVE-2022-26488
- https://security.netapp.com/advisory/ntap-20220419-0005/
