# [H] CVE-2024-29506

## Summary
Severity: High
Advisory: CVE-2024-29506
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-07-03
Source: https://osv.dev/vulnerability/CVE-2024-29506
Type: osv

## Details
Artifex Ghostscript before 10.03.0 has a stack-based buffer overflow in the pdfi_apply_filter() function via a long PDF filter name.

## References
- https://git.ghostscript.com/?p=ghostpdl.git%3Bh=77dc7f699beba606937b7ea23b50cf5974fa64b1
- https://www.openwall.com/lists/oss-security/2024/07/03/7
- https://bugs.ghostscript.com/show_bug.cgi?id=707510
