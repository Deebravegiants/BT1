# [M] CVE-2017-2625

## Summary
Severity: Medium
Advisory: CVE-2017-2625
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-07-27
Source: https://osv.dev/vulnerability/CVE-2017-2625
Type: osv

## Details
It was discovered that libXdmcp before 1.1.2 including used weak entropy to generate session keys. On a multi-user system using xdmcp, a local attacker could potentially use information available from the process list to brute force the key, allowing them to hijack other users' sessions.

## References
- https://lists.debian.org/debian-lts-announce/2019/11/msg00024.html
- http://www.securityfocus.com/bid/96480
- http://www.securitytracker.com/id/1037919
- https://access.redhat.com/errata/RHSA-2017:1865
- https://cgit.freedesktop.org/xorg/lib/libXdmcp/commit/?id=0554324ec6bbc2071f5d1f8ad211a1643e29eb1f
- https://security.gentoo.org/glsa/201704-03
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-2625
- https://www.x41-dsec.de/lab/advisories/x41-2017-001-xorg/
