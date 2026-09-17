# [M] CVE-2017-15371

## Summary
Severity: Medium
Advisory: CVE-2017-15371
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-10-16
Source: https://osv.dev/vulnerability/CVE-2017-15371
Type: osv

## Details
There is a reachable assertion abort in the function sox_append_comment() in formats.c in Sound eXchange (SoX) 14.4.2. A Crafted input will lead to a denial of service attack during conversion of an audio file.

## References
- https://lists.debian.org/debian-lts-announce/2017/11/msg00043.html
- https://lists.debian.org/debian-lts-announce/2019/03/msg00007.html
- https://security.gentoo.org/glsa/201810-02
- https://bugzilla.redhat.com/show_bug.cgi?id=1500570
