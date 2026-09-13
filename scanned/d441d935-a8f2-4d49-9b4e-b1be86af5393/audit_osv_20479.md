# [H] CVE-2021-3410

## Summary
Severity: High
Advisory: CVE-2021-3410
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-02-23
Source: https://osv.dev/vulnerability/CVE-2021-3410
Type: osv

## Details
A flaw was found in libcaca v0.99.beta19. A buffer overflow issue in caca_resize function in libcaca/caca/canvas.c may lead to local execution of arbitrary code in the user context.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6WFGYICNTMNDNMDDUV4G2RYFB5HNJCOV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PC7EGOEQ5C4OD66ZUJJIIYEXBTZOCMZX/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZSBCRN6EGQJUVOSD4OEEQ6XORHEM2CUL/
- https://github.com/cacalabs/libcaca/issues/52
- https://lists.debian.org/debian-lts-announce/2021/03/msg00006.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1928437
