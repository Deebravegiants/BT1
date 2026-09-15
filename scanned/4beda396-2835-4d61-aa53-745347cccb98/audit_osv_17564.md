# [H] CVE-2020-16600

## Summary
Severity: High
Advisory: CVE-2020-16600
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-12-09
Source: https://osv.dev/vulnerability/CVE-2020-16600
Type: osv

## Details
A Use After Free vulnerability exists in Artifex Software, Inc. MuPDF library 1.17.0-rc1 and earlier when a valid page was followed by a page with invalid pixmap dimensions, causing bander - a static - to point to previously freed memory instead of a newband_writer.

## References
- http://git.ghostscript.com/?p=mupdf.git%3Bh=96751b25462f83d6e16a9afaf8980b0c3f979c8b
- https://bugs.ghostscript.com/show_bug.cgi?id=702253
