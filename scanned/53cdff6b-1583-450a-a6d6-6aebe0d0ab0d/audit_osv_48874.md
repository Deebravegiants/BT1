# [H] CVE-2018-16802

## Summary
Severity: High
Advisory: CVE-2018-16802
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-09-10
Source: https://osv.dev/vulnerability/CVE-2018-16802
Type: osv

## Details
An issue was discovered in Artifex Ghostscript before 9.25. Incorrect "restoration of privilege" checking when running out of stack during exception handling could be used by attackers able to supply crafted PostScript to execute code using the "pipe" instruction. This is due to an incomplete fix for CVE-2018-16509.

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=3e5d316b72e3965b7968bb1d96baa137cd063ac6
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=643b24dbd002fb9c131313253c307cf3951b3d47
- https://git.ghostscript.com/?p=ghostpdl.git%3Ba=commitdiff%3Bh=5812b1b78fc4d36fdc293b7859de69241140d590
- https://www.debian.org/security/2018/dsa-4294
- https://access.redhat.com/errata/RHSA-2018:3834
- https://lists.debian.org/debian-lts-announce/2018/09/msg00015.html
- https://security.gentoo.org/glsa/201811-12
- https://usn.ubuntu.com/3768-1/
- https://seclists.org/oss-sec/2018/q3/228
- https://seclists.org/oss-sec/2018/q3/229
