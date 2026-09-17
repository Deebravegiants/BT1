# [H] CVE-2017-9727

## Summary
Severity: High
Advisory: CVE-2017-9727
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-07-26
Source: https://osv.dev/vulnerability/CVE-2017-9727
Type: osv

## Details
The gx_ttfReader__Read function in base/gxttfb.c in Artifex Ghostscript GhostXPS 9.21 allows remote attackers to cause a denial of service (heap-based buffer over-read and application crash) or possibly have unspecified other impact via a crafted document.

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=937ccd17ac65935633b2ebc06cb7089b91e17e6b
- http://www.debian.org/security/2017/dsa-3986
- http://www.securityfocus.com/bid/99999
- https://security.gentoo.org/glsa/201811-12
- http://bugs.ghostscript.com/show_bug.cgi?id=698056
