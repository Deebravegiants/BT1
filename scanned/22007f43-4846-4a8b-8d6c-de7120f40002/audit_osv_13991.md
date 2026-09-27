# [M] CVE-2018-6192

## Summary
Severity: Medium
Advisory: CVE-2018-6192
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-01-24
Source: https://osv.dev/vulnerability/CVE-2018-6192
Type: osv

## Details
In Artifex MuPDF 1.12.0, the pdf_read_new_xref function in pdf/pdf-xref.c allows remote attackers to cause a denial of service (segmentation violation and application crash) via a crafted pdf file.

## References
- https://cgit.ghostscript.com/cgi-bin/cgit.cgi/mupdf.git/commit/?id=5e411a99604ff6be5db9e273ee84737204113299
- https://lists.debian.org/debian-lts-announce/2019/06/msg00027.html
- http://www.securityfocus.com/bid/102822
- https://security.gentoo.org/glsa/201811-15
- https://www.debian.org/security/2018/dsa-4334
- https://bugs.ghostscript.com/show_bug.cgi?id=698916
