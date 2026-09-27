# [H] BIT-libpython-2021-3737

## Summary
Severity: High
Advisory: BIT-libpython-2021-3737
Aliases: BIT-python-2021-3737, BIT-python-min-2021-3737, CVE-2021-3737, PSF-2022-7
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libpython-2021-3737
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.9.0 <3.9.6

## Details
A flaw was found in python. An improperly handled HTTP response in the HTTP client code of python may allow a remote attacker, who controls the HTTP server, to make the client script enter an infinite loop, consuming CPU time. The highest threat from this vulnerability is to system availability.

## References
- https://bugs.python.org/issue44022
- https://bugzilla.redhat.com/show_bug.cgi?id=1995162
- https://github.com/python/cpython/pull/25916
- https://github.com/python/cpython/pull/26503
- https://lists.debian.org/debian-lts-announce/2023/05/msg00024.html
- https://lists.debian.org/debian-lts-announce/2023/06/msg00039.html
- https://nvd.nist.gov/vuln/detail/CVE-2021-3737
- https://python-security.readthedocs.io/vuln/urllib-100-continue-loop.html
- https://security.netapp.com/advisory/ntap-20220407-0009/
- https://ubuntu.com/security/CVE-2021-3737
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://lists.debian.org/debian-lts-announce/2024/11/msg00024.html
- https://lists.debian.org/debian-lts-announce/2024/12/msg00000.html
