# [M] BIT-libpython-2024-50602

## Summary
Severity: Medium
Advisory: BIT-libpython-2024-50602
Aliases: BIT-python-2024-50602, BIT-python-min-2024-50602, CVE-2024-50602
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libpython-2024-50602
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.13.0 <3.13.1

## Details
An issue was discovered in libexpat before 2.6.4. There is a crash within the XML_ResumeParser function because XML_StopParser can stop/suspend an unstarted parser.

## References
- https://github.com/libexpat/libexpat/pull/915
- https://lists.debian.org/debian-lts-announce/2025/04/msg00040.html
- https://nvd.nist.gov/vuln/detail/CVE-2024-50602
- https://security.netapp.com/advisory/ntap-20250404-0008/
- https://docs.python.org/release/3.10.16/whatsnew/changelog.html
- https://docs.python.org/release/3.11.11/whatsnew/changelog.html#python-3-11-11
- https://docs.python.org/release/3.12.8/whatsnew/changelog.html#python-3-12-8
- https://docs.python.org/release/3.13.1/whatsnew/changelog.html#python-3-13-1
- https://docs.python.org/release/3.9.21/whatsnew/changelog.html
- https://github.com/python/cpython/issues/126623
