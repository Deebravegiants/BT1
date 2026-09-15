# [M] CVE-2018-6187

## Summary
Severity: Medium
Advisory: CVE-2018-6187
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-01-24
Source: https://osv.dev/vulnerability/CVE-2018-6187
Type: osv

## Details
In Artifex MuPDF 1.12.0, there is a heap-based buffer overflow vulnerability in the do_pdf_save_document function in the pdf/pdf-write.c file. Remote attackers could leverage the vulnerability to cause a denial of service via a crafted pdf file.

## References
- https://cgit.ghostscript.com/cgi-bin/cgit.cgi/mupdf.git/commit/?id=3e30fbb7bf5efd88df431e366492356e7eb969ec
- http://www.securityfocus.com/bid/102823
- https://security.gentoo.org/glsa/201811-15
- https://www.debian.org/security/2018/dsa-4334
- https://bugs.ghostscript.com/show_bug.cgi?id=698908
