# [H] CVE-2018-15909

## Summary
Severity: High
Advisory: CVE-2018-15909
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-08-27
Source: https://osv.dev/vulnerability/CVE-2018-15909
Type: osv

## Details
In Artifex Ghostscript 9.23 before 2018-08-24, a type confusion using the .shfill operator could be used by attackers able to supply crafted PostScript files to crash the interpreter or potentially execute code.

## References
- https://support.f5.com/csp/article/K24803507?utm_source=f5support&amp%3Butm_medium=RSS
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=0b6cd1918e1ec4ffd087400a754a845180a4522b
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=e01e77a36cbb2e0277bc3a63852244bec41be0f6
- https://usn.ubuntu.com/3768-1/
- http://www.securityfocus.com/bid/105178
- https://access.redhat.com/errata/RHSA-2018:3650
- https://lists.debian.org/debian-lts-announce/2018/09/msg00015.html
- https://security.gentoo.org/glsa/201811-12
- https://www.kb.cert.org/vuls/id/332928
- https://kb.pulsesecure.net/articles/Pulse_Security_Advisories/SA44101
