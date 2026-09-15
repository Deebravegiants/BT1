# [H] CVE-2017-11714

## Summary
Severity: High
Advisory: CVE-2017-11714
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-07-28
Source: https://osv.dev/vulnerability/CVE-2017-11714
Type: osv

## Details
psi/ztoken.c in Artifex Ghostscript 9.21 mishandles references to the scanner state structure, which allows remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact via a crafted PostScript document, related to an out-of-bounds read in the igc_reloc_struct_ptr function in psi/igc.c.

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=671fd59eb657743aa86fbc1895cb15872a317caa
- http://www.debian.org/security/2017/dsa-3986
- http://www.securitytracker.com/id/1039233
- https://security.gentoo.org/glsa/201811-12
- https://bugs.ghostscript.com/show_bug.cgi?id=698158
