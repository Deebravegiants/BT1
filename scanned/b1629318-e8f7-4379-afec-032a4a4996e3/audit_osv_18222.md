# [H] CVE-2020-25219

## Summary
Severity: High
Advisory: CVE-2020-25219
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-09-09
Source: https://osv.dev/vulnerability/CVE-2020-25219
Type: osv

## Details
url::recvline in url.cpp in libproxy 0.4.x through 0.4.15 allows a remote HTTP server to trigger uncontrolled recursion via a response composed of an infinite stream that lacks a newline character. This leads to stack exhaustion.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CNID6EZVOVH7EZB7KFU2EON54CFDIVUR/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JF5JSONJNO64ARWRVOS6K6HSIPHEF3H2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SSVZAAVHBJR3Z4MZNR55QW3OQFAS2STH/
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00030.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00033.html
- https://lists.debian.org/debian-lts-announce/2020/09/msg00012.html
- https://usn.ubuntu.com/4514-1/
- https://www.debian.org/security/2020/dsa-4800
- https://github.com/libproxy/libproxy/issues/134
