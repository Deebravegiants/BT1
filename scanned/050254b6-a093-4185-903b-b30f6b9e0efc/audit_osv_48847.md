# [H] CVE-2018-15911

## Summary
Severity: High
Advisory: CVE-2018-15911
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-08-28
Source: https://osv.dev/vulnerability/CVE-2018-15911
Type: osv

## Details
In Artifex Ghostscript 9.23 before 2018-08-24, attackers able to supply crafted PostScript could use uninitialized memory access in the aesdecode operator to crash the interpreter or potentially execute code.

## References
- https://support.f5.com/csp/article/K22141757?utm_source=f5support&amp%3Butm_medium=RSS
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=8e9ce5016db968b40e4ec255a3005f2786cce45f
- https://security.gentoo.org/glsa/201811-12
- http://www.securityfocus.com/bid/105122
- https://access.redhat.com/errata/RHSA-2018:3834
- https://lists.debian.org/debian-lts-announce/2018/09/msg00015.html
- https://usn.ubuntu.com/3768-1/
- https://www.debian.org/security/2018/dsa-4288
- https://bugs.ghostscript.com/show_bug.cgi?id=699665
- https://www.kb.cert.org/vuls/id/332928
- https://kb.pulsesecure.net/articles/Pulse_Security_Advisories/SA44101
