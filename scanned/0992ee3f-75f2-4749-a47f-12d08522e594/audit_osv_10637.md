# [H] CVE-2017-17858

## Summary
Severity: High
Advisory: CVE-2017-17858
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-01-22
Source: https://osv.dev/vulnerability/CVE-2017-17858
Type: osv

## Details
Heap-based buffer overflow in the ensure_solid_xref function in pdf/pdf-xref.c in Artifex MuPDF 1.12.0 allows a remote attacker to potentially execute arbitrary code via a crafted PDF file, because xref subsection object numbers are unrestricted.

## References
- http://git.ghostscript.com/?p=mupdf.git%3Ba=commit%3Bh=55c3f68d638ac1263a386e0aaa004bb6e8bde731
- https://security.gentoo.org/glsa/201811-15
- https://bugs.ghostscript.com/show_bug.cgi?id=698819
- https://github.com/mzet-/Security-Advisories/blob/master/mzet-adv-2017-01.md
