# [M] Quoted zip-bomb protection for zipfile

## Summary
Severity: Medium
Advisory: BIT-libpython-2024-0450
Aliases: BIT-python-2024-0450, BIT-python-min-2024-0450, CVE-2024-0450, PSF-2024-2
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libpython-2024-0450
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.12.0 <3.12.2

## Details
An issue was found in the CPython `zipfile` module affecting versions 3.12.1, 3.11.7, 3.10.13, 3.9.18, and 3.8.18 and prior.

The zipfile module is vulnerable to “quoted-overlap” zip-bombs which exploit the zip format to create a zip-bomb with a high compression ratio. The fixed versions of CPython makes the zipfile module reject zip archives which overlap entries in the archive.

## References
- http://www.openwall.com/lists/oss-security/2024/03/20/5
- https://github.com/python/cpython/commit/30fe5d853b56138dbec62432d370a1f99409fc85
- https://github.com/python/cpython/commit/66363b9a7b9fe7c99eba3a185b74c5fdbf842eba
- https://github.com/python/cpython/commit/70497218351ba44bffc8b571201ecb5652d84675
- https://github.com/python/cpython/commit/a2c59992e9e8d35baba9695eb186ad6c6ff85c51
- https://github.com/python/cpython/commit/a956e510f6336d5ae111ba429a61c3ade30a7549
- https://github.com/python/cpython/commit/d05bac0b74153beb541b88b4fca33bf053990183
- https://github.com/python/cpython/commit/fa181fcf2156f703347b03a3b1966ce47be8ab3b
- https://github.com/python/cpython/issues/109858
- https://lists.debian.org/debian-lts-announce/2024/03/msg00024.html
- https://lists.debian.org/debian-lts-announce/2024/03/msg00025.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/T3IGRX54M7RNCQOXVQO5KQKTGWCOABIM/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/U5VHWS52HGD743C47UMCSAK2A773M2YE/
- https://mail.python.org/archives/list/security-announce@python.org/thread/XELNUX2L3IOHBTFU7RQHCY6OUVEWZ2FG/
- https://nvd.nist.gov/vuln/detail/CVE-2024-0450
- https://security.netapp.com/advisory/ntap-20250411-0005/
- https://www.bamsoftware.com/hacks/zipbomb/
- https://lists.debian.org/debian-lts-announce/2024/11/msg00005.html
- https://lists.debian.org/debian-lts-announce/2024/12/msg00000.html
