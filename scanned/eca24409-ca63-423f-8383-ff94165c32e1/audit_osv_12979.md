# [M] CVE-2018-16647

## Summary
Severity: Medium
Advisory: CVE-2018-16647
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-09-06
Source: https://osv.dev/vulnerability/CVE-2018-16647
Type: osv

## Details
In Artifex MuPDF 1.13.0, the pdf_get_xref_entry function in pdf/pdf-xref.c allows remote attackers to cause a denial of service (segmentation fault in fz_write_data in fitz/output.c) via a crafted pdf file.

## References
- https://cgit.ghostscript.com/cgi-bin/cgit.cgi/mupdf.git/commit/?id=351c99d8ce23bbf7099dbd52771a095f67e45a2c
- https://lists.debian.org/debian-lts-announce/2020/07/msg00019.html
- https://bugs.ghostscript.com/show_bug.cgi?id=699686
