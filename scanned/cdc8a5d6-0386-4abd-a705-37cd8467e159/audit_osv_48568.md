# [H] CVE-2017-9619

## Summary
Severity: High
Advisory: CVE-2017-9619
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-07-26
Source: https://osv.dev/vulnerability/CVE-2017-9619
Type: osv

## Details
The xps_true_callback_glyph_name function in xps/xpsttf.c in Artifex Ghostscript GhostXPS 9.21 allows remote attackers to cause a denial of service (Segmentation Violation and application crash) via a crafted file.

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=c53183d4e7103e87368b7cfa15367a47d559e323
- https://security.gentoo.org/glsa/201811-12
- http://www.securityfocus.com/bid/99988
- https://bugs.ghostscript.com/show_bug.cgi?id=698042
