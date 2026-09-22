# [H] CVE-2019-12109

## Summary
Severity: High
Advisory: CVE-2019-12109
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-05-15
Source: https://osv.dev/vulnerability/CVE-2019-12109
Type: osv

## Details
A Denial Of Service vulnerability in MiniUPnP MiniUPnPd through 2.1 exists due to a NULL pointer dereference in GetOutboundPinholeTimeout in upnpsoap.c for rem_port.

## References
- https://lists.debian.org/debian-lts-announce/2019/05/msg00045.html
- https://usn.ubuntu.com/4542-1/
- https://github.com/miniupnp/miniupnp/commit/13585f15c7f7dc28bbbba1661efb280d530d114c
- https://github.com/miniupnp/miniupnp/commit/86030db849260dd8fb2ed975b9890aef1b62b692
- https://www.vdoo.com/blog/security-issues-discovered-in-miniupnp
