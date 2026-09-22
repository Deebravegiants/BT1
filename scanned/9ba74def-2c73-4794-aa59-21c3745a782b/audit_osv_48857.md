# [H] CVE-2018-16513

## Summary
Severity: High
Advisory: CVE-2018-16513
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-09-05
Source: https://osv.dev/vulnerability/CVE-2018-16513
Type: osv

## Details
In Artifex Ghostscript before 9.24, attackers able to supply crafted PostScript files could use a type confusion in the setcolor function to crash the interpreter or possibly have unspecified other impact.

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=b326a71659b7837d3acde954b18bda1a6f5e9498
- https://support.f5.com/csp/article/K22141757?utm_source=f5support&amp%3Butm_medium=RSS
- https://lists.debian.org/debian-lts-announce/2018/09/msg00015.html
- https://security.gentoo.org/glsa/201811-12
- https://usn.ubuntu.com/3768-1/
- https://www.debian.org/security/2018/dsa-4288
- https://bugs.ghostscript.com/show_bug.cgi?id=699655
- https://kb.pulsesecure.net/articles/Pulse_Security_Advisories/SA44101
- https://www.artifex.com/news/ghostscript-security-resolved/
