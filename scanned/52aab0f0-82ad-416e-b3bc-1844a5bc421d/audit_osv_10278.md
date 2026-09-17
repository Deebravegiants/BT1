# [H] CVE-2017-14687

## Summary
Severity: High
Advisory: CVE-2017-14687
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-09-22
Source: https://osv.dev/vulnerability/CVE-2017-14687
Type: osv

## Details
Artifex MuPDF 1.11 allows attackers to cause a denial of service or possibly have unspecified other impact via a crafted .xps file, related to "Data from Faulting Address controls Branch Selection starting at mupdf+0x000000000016cb4f" on Windows. This occurs because of mishandling of XML tag name comparisons.

## References
- http://git.ghostscript.com/?p=mupdf.git%3Bh=2b16dbd8f73269cb15ca61ece75cf8d2d196ed28
- https://lists.debian.org/debian-lts-announce/2017/11/msg00007.html
- http://www.debian.org/security/2017/dsa-4006
- https://github.com/wlinzi/security_advisories/tree/master/CVE-2017-14687
- https://bugs.ghostscript.com/show_bug.cgi?id=698558
