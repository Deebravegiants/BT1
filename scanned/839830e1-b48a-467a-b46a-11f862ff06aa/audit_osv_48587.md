# [H] CVE-2017-9835

## Summary
Severity: High
Advisory: CVE-2017-9835
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-07-26
Source: https://osv.dev/vulnerability/CVE-2017-9835
Type: osv

## Details
The gs_alloc_ref_array function in psi/ialloc.c in Artifex Ghostscript 9.21 allows remote attackers to cause a denial of service (heap-based buffer overflow and application crash) or possibly have unspecified other impact via a crafted PostScript document. This is related to a lack of an integer overflow check in base/gsalloc.c.

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=cfde94be1d4286bc47633c6e6eaf4e659bd78066
- http://www.debian.org/security/2017/dsa-3986
- http://www.securityfocus.com/bid/99991
- https://security.gentoo.org/glsa/201811-12
- https://bugs.ghostscript.com/show_bug.cgi?id=697985
