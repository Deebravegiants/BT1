# [H] CVE-2017-7948

## Summary
Severity: High
Advisory: CVE-2017-7948
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-04-19
Source: https://osv.dev/vulnerability/CVE-2017-7948
Type: osv

## Details
Integer overflow in the mark_curve function in Artifex Ghostscript 9.21 allows remote attackers to cause a denial of service (out-of-bounds write and application crash) or possibly have unspecified other impact via a crafted PostScript document.

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Bh=8210a2864372723b49c526e2b102fdc00c9c4699
- https://security.gentoo.org/glsa/201811-12
- https://bugs.ghostscript.com/show_bug.cgi?id=697762
