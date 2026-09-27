# [H] CVE-2017-5991

## Summary
Severity: High
Advisory: CVE-2017-5991
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-02-15
Source: https://osv.dev/vulnerability/CVE-2017-5991
Type: osv

## Details
An issue was discovered in Artifex MuPDF before 1912de5f08e90af1d9d0a9791f58ba3afdb9d465. The pdf_run_xobject function in pdf-op-run.c encounters a NULL pointer dereference during a Fitz fz_paint_pixmap_with_mask painting operation. Versions 1.11 and later are unaffected.

## References
- http://git.ghostscript.com/?p=mupdf.git%3Bh=1912de5f08e90af1d9d0a9791f58ba3afdb9d465
- http://www.securityfocus.com/bid/96213
- http://www.debian.org/security/2017/dsa-3797
- https://security.gentoo.org/glsa/201706-08
- https://bugs.ghostscript.com/show_bug.cgi?id=697500
- https://www.exploit-db.com/exploits/42138/
