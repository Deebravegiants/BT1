# [H] BIT-libpython-2023-6597

## Summary
Severity: High
Advisory: BIT-libpython-2023-6597
Aliases: BIT-python-2023-6597, BIT-python-min-2023-6597, CVE-2023-6597, PSF-2024-1
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libpython-2023-6597
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.12.0 <3.12.1

## Details
An issue was found in the CPython `tempfile.TemporaryDirectory` class affecting versions 3.12.1, 3.11.7, 3.10.13, 3.9.18, and 3.8.18 and prior.

The tempfile.TemporaryDirectory class would dereference symlinks during cleanup of permissions-related errors. This means users which can run privileged programs are potentially able to modify permissions of files referenced by symlinks in some circumstances.

## References
- http://www.openwall.com/lists/oss-security/2024/03/20/5
- https://github.com/python/cpython/commit/02a9259c717738dfe6b463c44d7e17f2b6d2cb3a
- https://github.com/python/cpython/commit/5585334d772b253a01a6730e8202ffb1607c3d25
- https://github.com/python/cpython/commit/6ceb8aeda504b079fef7a57b8d81472f15cdd9a5
- https://github.com/python/cpython/commit/81c16cd94ec38d61aa478b9a452436dc3b1b524d
- https://github.com/python/cpython/commit/8eaeefe49d179ca4908d052745e3bb8b6f238f82
- https://github.com/python/cpython/commit/d54e22a669ae6e987199bb5d2c69bb5a46b0083b
- https://github.com/python/cpython/issues/91133
- https://lists.debian.org/debian-lts-announce/2024/03/msg00025.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/T3IGRX54M7RNCQOXVQO5KQKTGWCOABIM/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/U5VHWS52HGD743C47UMCSAK2A773M2YE/
- https://mail.python.org/archives/list/security-announce@python.org/thread/Q5C6ATFC67K53XFV4KE45325S7NS62LD/
- https://nvd.nist.gov/vuln/detail/CVE-2023-6597
- https://lists.debian.org/debian-lts-announce/2024/11/msg00005.html
- https://lists.debian.org/debian-lts-announce/2024/12/msg00000.html
