# [H] CVE-2017-14685

## Summary
Severity: High
Advisory: CVE-2017-14685
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-09-22
Source: https://osv.dev/vulnerability/CVE-2017-14685
Type: osv

## Details
Artifex MuPDF 1.11 allows attackers to cause a denial of service or possibly have unspecified other impact via a crafted .xps file, related to "Data from Faulting Address controls Branch Selection starting at mupdf+0x000000000016aa61" on Windows. This occurs because xps_load_links_in_glyphs in xps/xps-link.c does not verify that an xps font could be loaded.

## References
- http://git.ghostscript.com/?p=mupdf.git%3Bh=ab1a420613dec93c686acbee2c165274e922f82a
- http://www.debian.org/security/2017/dsa-4006
- https://github.com/wlinzi/security_advisories/tree/master/CVE-2017-14685
- https://bugs.ghostscript.com/show_bug.cgi?id=698539
