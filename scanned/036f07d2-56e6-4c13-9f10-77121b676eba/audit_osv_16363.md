# [M] CVE-2019-6130

## Summary
Severity: Medium
Advisory: CVE-2019-6130
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-01-11
Source: https://osv.dev/vulnerability/CVE-2019-6130
Type: osv

## Details
Artifex MuPDF 1.14.0 has a SEGV in the function fz_load_page of the fitz/document.c file, as demonstrated by mutool. This is related to page-number mishandling in cbz/mucbz.c, cbz/muimg.c, and svg/svg-doc.c.

## References
- https://cgit.ghostscript.com/cgi-bin/cgit.cgi/mupdf.git/commit/?id=faf47b94e24314d74907f3f6bc874105f2c962ed
- https://lists.debian.org/debian-lts-announce/2019/06/msg00027.html
- https://lists.debian.org/debian-lts-announce/2020/07/msg00019.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CNJNEX5EW6YH5OARXXSSXW4HHC5PIBSY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SEK2EHVNREJ7XZMFF2MXRWKIF4IBHPNE/
- http://www.securityfocus.com/bid/106558
- https://bugs.ghostscript.com/show_bug.cgi?id=700446
