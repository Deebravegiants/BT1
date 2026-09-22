# [M] CVE-2018-6544

## Summary
Severity: Medium
Advisory: CVE-2018-6544
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-02-02
Source: https://osv.dev/vulnerability/CVE-2018-6544
Type: osv

## Details
pdf_load_obj_stm in pdf/pdf-xref.c in Artifex MuPDF 1.12.0 could reference the object stream recursively and therefore run out of error stack, which allows remote attackers to cause a denial of service via a crafted PDF document.

## References
- http://git.ghostscript.com/?p=mupdf.git%3Bh=26527eef77b3e51c2258c8e40845bfbc015e405d
- http://git.ghostscript.com/?p=mupdf.git%3Bh=b03def134988da8c800adac1a38a41a1f09a1d89
- https://security.gentoo.org/glsa/201811-15
- https://www.debian.org/security/2018/dsa-4152
- https://bugs.ghostscript.com/show_bug.cgi?id=698830
- https://bugs.ghostscript.com/show_bug.cgi?id=698965
