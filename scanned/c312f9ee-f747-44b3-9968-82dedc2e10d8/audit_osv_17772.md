# [M] CVE-2020-19609

## Summary
Severity: Medium
Advisory: CVE-2020-19609
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-07-21
Source: https://osv.dev/vulnerability/CVE-2020-19609
Type: osv

## Details
Artifex MuPDF before 1.18.0 has a heap based buffer over-write in tiff_expand_colormap() function when parsing TIFF files allowing attackers to cause a denial of service.

## References
- http://git.ghostscript.com/?p=mupdf.git%3Bh=b7892cdc7fae62aa57d63ae62144e1f11b5f9275
- https://lists.debian.org/debian-lts-announce/2021/09/msg00013.html
- https://bugs.ghostscript.com/show_bug.cgi?id=703076
- https://bugs.ghostscript.com/show_bug.cgi?id=701176
