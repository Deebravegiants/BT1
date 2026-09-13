# [H] CVE-2018-20546

## Summary
Severity: High
Advisory: CVE-2018-20546
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2018-12-28
Source: https://osv.dev/vulnerability/CVE-2018-20546
Type: osv

## Details
There is an illegal READ memory access at caca/dither.c (function get_rgba_default) in libcaca 0.99.beta19 for the default bpp case.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6WFGYICNTMNDNMDDUV4G2RYFB5HNJCOV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PC7EGOEQ5C4OD66ZUJJIIYEXBTZOCMZX/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZSBCRN6EGQJUVOSD4OEEQ6XORHEM2CUL/
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00033.html
- https://github.com/cacalabs/libcaca/issues/38
- https://lists.debian.org/debian-lts-announce/2019/01/msg00007.html
- https://usn.ubuntu.com/3860-1/
- https://usn.ubuntu.com/3860-2/
- https://bugzilla.redhat.com/show_bug.cgi?id=1652622
- https://github.com/cacalabs/libcaca/commit/1022d97496c7899e8641515af363381b31ae2f05
