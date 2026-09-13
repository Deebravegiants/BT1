# [M] CVE-2025-46646

## Summary
Severity: Medium
Advisory: CVE-2025-46646
CVSS: 4.5 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:N)
Published: 2025-04-26
Source: https://osv.dev/vulnerability/CVE-2025-46646
Type: osv

## Details
In Artifex Ghostscript before 10.05.0, decode_utf8 in base/gp_utf8.c mishandles overlong UTF-8 encoding. NOTE: this issue exists because of an incomplete fix for CVE-2024-46954.

## References
- https://bugs.ghostscript.com/show_bug.cgi?id=708311
- https://cgit.ghostscript.com/cgi-bin/cgit.cgi/ghostpdl.git/commit/?id=f14ea81e6c3d2f51593f23cdf13c4679a18f1a3f
