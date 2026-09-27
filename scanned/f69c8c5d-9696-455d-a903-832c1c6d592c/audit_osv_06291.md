# [M] BIT-libpython-2021-3733

## Summary
Severity: Medium
Advisory: BIT-libpython-2021-3733
Aliases: BIT-python-2021-3733, BIT-python-min-2021-3733, CVE-2021-3733, PSF-2022-6
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libpython-2021-3733
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.9.0 <3.9.5

## Details
There's a flaw in urllib's AbstractBasicAuthHandler class. An attacker who controls a malicious HTTP server that an HTTP client (such as web browser) connects to, could trigger a Regular Expression Denial of Service (ReDOS) during an authentication request with a specially crafted payload that is sent by the server to the client. The greatest threat that this flaw poses is to application availability.

## References
- https://bugs.python.org/issue43075
- https://bugzilla.redhat.com/show_bug.cgi?id=1995234
- https://github.com/python/cpython/commit/7215d1ae25525c92b026166f9d5cac85fb
- https://github.com/python/cpython/pull/24391
- https://lists.debian.org/debian-lts-announce/2023/05/msg00024.html
- https://lists.debian.org/debian-lts-announce/2023/06/msg00039.html
- https://nvd.nist.gov/vuln/detail/CVE-2021-3733
- https://security.netapp.com/advisory/ntap-20220407-0001/
- https://ubuntu.com/security/CVE-2021-3733
- https://lists.debian.org/debian-lts-announce/2024/12/msg00000.html
