# [H] CVE-2017-2624

## Summary
Severity: High
Advisory: CVE-2017-2624
CVSS: 7.0 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-27
Source: https://osv.dev/vulnerability/CVE-2017-2624
Type: osv

## Details
It was found that xorg-x11-server before 1.19.0 including uses memcmp() to check the received MIT cookie against a series of valid cookies. If the cookie is correct, it is allowed to attach to the Xorg session. Since most memcmp() implementations return after an invalid byte is seen, this causes a time difference between a valid and invalid byte, which could allow an efficient brute force attack.

## References
- http://www.securityfocus.com/bid/96480
- http://www.securitytracker.com/id/1037919
- https://lists.debian.org/debian-lts-announce/2017/11/msg00032.html
- https://security.gentoo.org/glsa/201704-03
- https://security.gentoo.org/glsa/201710-30
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-2624
- https://gitlab.freedesktop.org/xorg/xserver/commit/d7ac755f0b618eb1259d93c8a16ec6e39a18627c
- https://www.x41-dsec.de/lab/advisories/x41-2017-001-xorg/
