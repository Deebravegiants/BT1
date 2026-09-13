# [M] CVE-2018-5686

## Summary
Severity: Medium
Advisory: CVE-2018-5686
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-01-14
Source: https://osv.dev/vulnerability/CVE-2018-5686
Type: osv

## Details
In MuPDF 1.12.0, there is an infinite loop vulnerability and application hang in the pdf_parse_array function (pdf/pdf-parse.c) because EOF is not considered. Remote attackers could leverage this vulnerability to cause a denial of service via a crafted pdf file.

## References
- https://cgit.ghostscript.com/cgi-bin/cgit.cgi/mupdf.git/commit/?id=b70eb93f6936c03d8af52040bbca4d4a7db39079
- https://lists.debian.org/debian-lts-announce/2019/06/msg00027.html
- https://security.gentoo.org/glsa/201811-15
- https://www.debian.org/security/2018/dsa-4334
- https://bugs.ghostscript.com/show_bug.cgi?id=698860
