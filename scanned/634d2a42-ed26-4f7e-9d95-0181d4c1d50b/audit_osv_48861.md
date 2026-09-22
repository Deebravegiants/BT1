# [M] CVE-2018-16542

## Summary
Severity: Medium
Advisory: CVE-2018-16542
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-09-05
Source: https://osv.dev/vulnerability/CVE-2018-16542
Type: osv

## Details
In Artifex Ghostscript before 9.24, attackers able to supply crafted PostScript files could use insufficient interpreter stack-size checking during error handling to crash the interpreter.

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=b575e1ec42cc86f6a58c603f2a88fcc2af699cc8
- https://www.debian.org/security/2018/dsa-4288
- http://seclists.org/oss-sec/2018/q3/182
- http://www.securityfocus.com/bid/105337
- https://access.redhat.com/errata/RHSA-2018:2918
- https://lists.debian.org/debian-lts-announce/2018/09/msg00015.html
- https://security.gentoo.org/glsa/201811-12
- https://usn.ubuntu.com/3768-1/
- https://bugs.ghostscript.com/show_bug.cgi?id=699668
