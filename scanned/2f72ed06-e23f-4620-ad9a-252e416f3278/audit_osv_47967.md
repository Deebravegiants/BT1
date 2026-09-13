# [M] CVE-2017-15642

## Summary
Severity: Medium
Advisory: CVE-2017-15642
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-10-19
Source: https://osv.dev/vulnerability/CVE-2017-15642
Type: osv

## Details
In lsx_aiffstartread in aiff.c in Sound eXchange (SoX) 14.4.2, there is a Use-After-Free vulnerability triggered by supplying a malformed AIFF file.

## References
- https://security.gentoo.org/glsa/201810-02
- https://lists.debian.org/debian-lts-announce/2017/11/msg00043.html
- https://lists.debian.org/debian-lts-announce/2019/02/msg00042.html
- https://sourceforge.net/p/sox/bugs/297/
- https://sourceforge.net/p/sox/bugs/298/
