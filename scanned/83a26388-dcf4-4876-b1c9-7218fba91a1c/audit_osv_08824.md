# [M] CVE-2016-6265

## Summary
Severity: Medium
Advisory: CVE-2016-6265
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-09-22
Source: https://osv.dev/vulnerability/CVE-2016-6265
Type: osv

## Details
Use-after-free vulnerability in the pdf_load_xref function in pdf/pdf-xref.c in MuPDF allows remote attackers to cause a denial of service (crash) via a crafted PDF file.

## References
- http://git.ghostscript.com/?p=mupdf.git%3Bh=fa1936405b6a84e5c9bb440912c23d532772f958
- http://lists.opensuse.org/opensuse-updates/2016-08/msg00007.html
- http://www.debian.org/security/2016/dsa-3655
- http://www.securityfocus.com/bid/92071
- https://security.gentoo.org/glsa/201702-12
- http://bugs.ghostscript.com/show_bug.cgi?id=696941
- http://www.openwall.com/lists/oss-security/2016/07/21/7
