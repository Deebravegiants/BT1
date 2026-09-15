# [M] CVE-2017-5896

## Summary
Severity: Medium
Advisory: CVE-2017-5896
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-15
Source: https://osv.dev/vulnerability/CVE-2017-5896
Type: osv

## Details
Heap-based buffer overflow in the fz_subsample_pixmap function in fitz/pixmap.c in MuPDF 1.10a allows remote attackers to cause a denial of service (out-of-bounds read and crash) via a crafted image.

## References
- http://git.ghostscript.com/?p=mupdf.git%3Bh=2c4e5867ee699b1081527bc6c6ea0e99a35a5c27
- http://www.debian.org/security/2017/dsa-3797
- http://www.securityfocus.com/bid/96139
- https://security.gentoo.org/glsa/201702-12
- http://www.openwall.com/lists/oss-security/2017/02/06/3
- http://www.openwall.com/lists/oss-security/2017/02/07/1
- https://bugs.ghostscript.com/show_bug.cgi?id=697515
