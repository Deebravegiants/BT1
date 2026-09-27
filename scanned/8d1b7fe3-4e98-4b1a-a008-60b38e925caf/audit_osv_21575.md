# [M] CVE-2021-44225

## Summary
Severity: Medium
Advisory: CVE-2021-44225
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2021-11-26
Source: https://osv.dev/vulnerability/CVE-2021-44225
Type: osv

## Details
In Keepalived through 2.2.4, the D-Bus policy does not sufficiently restrict the message destination, allowing any user to inspect and manipulate any property. This leads to access-control bypass in some situations in which an unrelated D-Bus system service has a settable (writable) property

## References
- https://lists.debian.org/debian-lts-announce/2023/04/msg00012.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5226RYNMNB7FL4MSJDIBBGPUWH6LMRYV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6O2R6EXURJQFPFPYFWRCZLUYVWQCLSZM/
- https://github.com/acassen/keepalived/pull/2063
- https://github.com/acassen/keepalived/commit/7977fec0be89ae6fe87405b3f8da2f0b5e415e3d
