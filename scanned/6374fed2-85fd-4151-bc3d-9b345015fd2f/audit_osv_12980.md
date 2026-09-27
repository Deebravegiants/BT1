# [M] CVE-2018-16648

## Summary
Severity: Medium
Advisory: CVE-2018-16648
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-09-06
Source: https://osv.dev/vulnerability/CVE-2018-16648
Type: osv

## Details
In Artifex MuPDF 1.13.0, the fz_append_byte function in fitz/buffer.c allows remote attackers to cause a denial of service (segmentation fault) via a crafted pdf file. This is caused by a pdf/pdf-device.c pdf_dev_alpha array-index underflow.

## References
- https://cgit.ghostscript.com/cgi-bin/cgit.cgi/mupdf.git/commit/?id=38f883fe129a5e89306252a4676eaaf4bc968824
- https://lists.debian.org/debian-lts-announce/2020/07/msg00019.html
- https://bugs.ghostscript.com/show_bug.cgi?id=699685
