# [H] CVE-2019-14975

## Summary
Severity: High
Advisory: CVE-2019-14975
CVSS: 7.1 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2019-08-14
Source: https://osv.dev/vulnerability/CVE-2019-14975
Type: osv

## Details
Artifex MuPDF before 1.16.0 has a heap-based buffer over-read in fz_chartorune in fitz/string.c because pdf/pdf-op-filter.c does not check for a missing string.

## References
- http://git.ghostscript.com/?p=mupdf.git%3Ba=commit%3Bh=97096297d409ec6f206298444ba00719607e8ba8
- https://bugs.ghostscript.com/show_bug.cgi?id=701292
