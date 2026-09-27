# [M] CVE-2018-0360

## Summary
Severity: Medium
Advisory: CVE-2018-0360
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-07-16
Source: https://osv.dev/vulnerability/CVE-2018-0360
Type: osv

## Details
ClamAV before 0.100.1 has an HWP integer overflow with a resultant infinite loop via a crafted Hangul Word Processor file. This is in parsehwp3_paragraph() in libclamav/hwp.c.

## References
- http://www.securitytracker.com/id/1041367
- https://blog.clamav.net/2018/07/clamav-01001-has-been-released.html
- https://lists.debian.org/debian-lts-announce/2018/08/msg00020.html
- https://secuniaresearch.flexerasoftware.com/secunia_research/2018-12/
- https://security.gentoo.org/glsa/201904-12
- https://usn.ubuntu.com/3722-1/
- https://usn.ubuntu.com/3722-2/
