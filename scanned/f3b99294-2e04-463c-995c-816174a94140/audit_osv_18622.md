# [M] CVE-2020-29129

## Summary
Severity: Medium
Advisory: CVE-2020-29129
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-11-26
Source: https://osv.dev/vulnerability/CVE-2020-29129
Type: osv

## Details
ncsi.c in libslirp through 4.3.1 has a buffer over-read because it tries to read a certain amount of header data even if that exceeds the total packet length.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/45S5IHSWYITJKMRT23HCHJQDI674AMTQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OPCOHDEONMHH6QPJZKRLLCNRGRYODG7X/
- http://www.openwall.com/lists/oss-security/2020/11/27/1
- https://lists.debian.org/debian-lts-announce/2022/09/msg00008.html
- https://lists.freedesktop.org/archives/slirp/2020-November/000115.html
