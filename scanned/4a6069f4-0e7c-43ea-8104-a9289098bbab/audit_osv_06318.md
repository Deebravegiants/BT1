# [M] Email header injection due to unquoted newlines

## Summary
Severity: Medium
Advisory: BIT-libpython-2024-6923
Aliases: BIT-python-2024-6923, BIT-python-min-2024-6923, CVE-2024-6923, PSF-2024-8
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libpython-2024-6923
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.12.0 <3.12.5

## Details
There is a MEDIUM severity vulnerability affecting CPython.

The 
email module didn’t properly quote newlines for email headers when 
serializing an email message allowing for header injection when an email
 is serialized.

## References
- http://www.openwall.com/lists/oss-security/2024/08/01/3
- http://www.openwall.com/lists/oss-security/2024/08/02/2
- https://github.com/python/cpython/commit/06f28dc236708f72871c64d4bc4b4ea144c50147
- https://github.com/python/cpython/commit/097633981879b3c9de9a1dd120d3aa585ecc2384
- https://github.com/python/cpython/commit/4766d1200fdf8b6728137aa2927a297e224d5fa7
- https://github.com/python/cpython/commit/4aaa4259b5a6e664b7316a4d60bdec7ee0f124d0
- https://github.com/python/cpython/commit/b158a76ce094897c870fb6b3de62887b7ccc33f1
- https://github.com/python/cpython/commit/f7be505d137a22528cb0fc004422c0081d5d90e6
- https://github.com/python/cpython/commit/f7c0f09e69e950cf3c5ada9dbde93898eb975533
- https://github.com/python/cpython/issues/121650
- https://github.com/python/cpython/pull/122233
- https://lists.debian.org/debian-lts-announce/2025/01/msg00005.html
- https://mail.python.org/archives/list/security-announce@python.org/thread/QH3BUOE2DYQBWP7NAQ7UNHPPOELKISRW/
- https://nvd.nist.gov/vuln/detail/CVE-2024-6923
- https://security.netapp.com/advisory/ntap-20240926-0003/
- https://lists.debian.org/debian-lts-announce/2024/12/msg00000.html
