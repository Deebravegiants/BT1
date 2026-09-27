# [H] CVE-2018-10194

## Summary
Severity: High
Advisory: CVE-2018-10194
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-04-18
Source: https://osv.dev/vulnerability/CVE-2018-10194
Type: osv

## Details
The set_text_distance function in devices/vector/gdevpdts.c in the pdfwrite component in Artifex Ghostscript through 9.22 does not prevent overflows in text-positioning calculation, which allows remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact via a crafted PDF document.

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=39b1e54b2968620723bf32e96764c88797714879
- http://www.securitytracker.com/id/1040729
- https://access.redhat.com/errata/RHSA-2018:2918
- https://lists.debian.org/debian-lts-announce/2018/04/msg00028.html
- https://security.gentoo.org/glsa/201811-12
- https://usn.ubuntu.com/3636-1/
- https://bugs.ghostscript.com/show_bug.cgi?id=699255
