# [M] BIT-libpython-2021-4189

## Summary
Severity: Medium
Advisory: BIT-libpython-2021-4189
Aliases: BIT-python-2021-4189, BIT-python-min-2021-4189, CVE-2021-4189
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libpython-2021-4189
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.10.0 <3.10.1

## Details
A flaw was found in Python, specifically in the FTP (File Transfer Protocol) client library in PASV (passive) mode. The issue is how the FTP client trusts the host from the PASV response by default. This flaw allows an attacker to set up a malicious FTP server that can trick FTP clients into connecting back to a given IP address and port. This vulnerability could lead to FTP client scanning ports, which otherwise would not have been possible.

## References
- https://access.redhat.com/security/cve/CVE-2021-4189
- https://bugs.python.org/issue43285
- https://bugzilla.redhat.com/show_bug.cgi?id=2036020
- https://github.com/python/cpython/commit/0ab152c6b5d95caa2dc1a30fa96e10258b5f188e
- https://lists.debian.org/debian-lts-announce/2023/05/msg00024.html
- https://lists.debian.org/debian-lts-announce/2023/06/msg00039.html
- https://nvd.nist.gov/vuln/detail/CVE-2021-4189
- https://python-security.readthedocs.io/vuln/ftplib-pasv.html
- https://security-tracker.debian.org/tracker/CVE-2021-4189
- https://security.netapp.com/advisory/ntap-20221104-0004/
- https://lists.debian.org/debian-lts-announce/2024/12/msg00000.html
