# [H] CVE-2024-29509

## Summary
Severity: High
Advisory: CVE-2024-29509
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-07-03
Source: https://osv.dev/vulnerability/CVE-2024-29509
Type: osv

## Details
Artifex Ghostscript before 10.03.0 has a heap-based overflow when PDFPassword (e.g., for runpdf) has a \000 byte in the middle.

## References
- https://git.ghostscript.com/?p=ghostpdl.git%3Bh=917b3a71fb20748965254631199ad98210d6c2fb
- https://www.openwall.com/lists/oss-security/2024/07/03/7
- https://bugs.ghostscript.com/show_bug.cgi?id=707510
