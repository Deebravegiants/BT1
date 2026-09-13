# [H] CVE-2017-7264

## Summary
Severity: High
Advisory: CVE-2017-7264
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-03-26
Source: https://osv.dev/vulnerability/CVE-2017-7264
Type: osv

## Details
Use-after-free vulnerability in the fz_subsample_pixmap function in fitz/pixmap.c in Artifex MuPDF 1.10a allows remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact via a crafted document.

## References
- http://git.ghostscript.com/?p=mupdf.git%3Bh=2c4e5867ee699b1081527bc6c6ea0e99a35a5c27
- http://www.securityfocus.com/bid/97111
- https://bugs.ghostscript.com/show_bug.cgi?id=697515
- https://blogs.gentoo.org/ago/2017/02/09/mupdf-use-after-free-in-fz_subsample_pixmap-pixmap-c/
