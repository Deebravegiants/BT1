# [M] CVE-2019-6131

## Summary
Severity: Medium
Advisory: CVE-2019-6131
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-01-11
Source: https://osv.dev/vulnerability/CVE-2019-6131
Type: osv

## Details
svg-run.c in Artifex MuPDF 1.14.0 has infinite recursion with stack consumption in svg_run_use_symbol, svg_run_element, and svg_run_use, as demonstrated by mutool.

## References
- https://cgit.ghostscript.com/cgi-bin/cgit.cgi/mupdf.git/commit/?id=c8f7e48ff74720a5e984ae19d978a5ab4d5dde5b
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CNJNEX5EW6YH5OARXXSSXW4HHC5PIBSY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SEK2EHVNREJ7XZMFF2MXRWKIF4IBHPNE/
- http://www.securityfocus.com/bid/106558
- https://bugs.ghostscript.com/show_bug.cgi?id=700442
