# [M] CVE-2017-13721

## Summary
Severity: Medium
Advisory: CVE-2017-13721
CVSS: 4.7 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-10-10
Source: https://osv.dev/vulnerability/CVE-2017-13721
Type: osv

## Details
In X.Org Server (aka xserver and xorg-server) before 1.19.4, an attacker authenticated to an X server with the X shared memory extension enabled can cause aborts of the X server or replace shared memory segments of other X clients in the same session.

## References
- http://www.debian.org/security/2017/dsa-4000
- http://www.openwall.com/lists/oss-security/2017/10/04/10
- http://www.securityfocus.com/bid/101238
- https://cgit.freedesktop.org/xorg/xserver/commit/?id=b95f25af141d33a65f6f821ea9c003f66a01e1f1
- https://lists.x.org/archives/xorg-announce/2017-October/002808.html
- https://security.gentoo.org/glsa/201710-30
