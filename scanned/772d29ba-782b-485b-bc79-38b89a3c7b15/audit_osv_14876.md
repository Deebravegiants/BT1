# [H] CVE-2019-12111

## Summary
Severity: High
Advisory: CVE-2019-12111
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-05-15
Source: https://osv.dev/vulnerability/CVE-2019-12111
Type: osv

## Details
A Denial Of Service vulnerability in MiniUPnP MiniUPnPd through 2.1 exists due to a NULL pointer dereference in copyIPv6IfDifferent in pcpserver.c.

## References
- https://usn.ubuntu.com/4542-1/
- https://lists.debian.org/debian-lts-announce/2019/05/msg00045.html
- https://github.com/miniupnp/miniupnp/commit/cb8a02af7a5677cf608e86d57ab04241cf34e24f
- https://www.vdoo.com/blog/security-issues-discovered-in-miniupnp
