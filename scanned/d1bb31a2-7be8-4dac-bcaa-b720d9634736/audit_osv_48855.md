# [H] CVE-2018-16510

## Summary
Severity: High
Advisory: CVE-2018-16510
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-09-05
Source: https://osv.dev/vulnerability/CVE-2018-16510
Type: osv

## Details
An issue was discovered in Artifex Ghostscript before 9.24. Incorrect exec stack handling in the "CS" and "SC" PDF primitives could be used by remote attackers able to supply crafted PDFs to crash the interpreter or possibly have unspecified other impact.

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=ea735ba37dc0fd5f5622d031830b9a559dec1cc9
- https://security.gentoo.org/glsa/201811-12
- https://usn.ubuntu.com/3768-1/
- https://usn.ubuntu.com/3773-1/
- https://bugs.ghostscript.com/show_bug.cgi?id=699671
- http://openwall.com/lists/oss-security/2018/08/27/4
