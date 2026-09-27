# [H] CVE-2017-15369

## Summary
Severity: High
Advisory: CVE-2017-15369
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-10-16
Source: https://osv.dev/vulnerability/CVE-2017-15369
Type: osv

## Details
The build_filter_chain function in pdf/pdf-stream.c in Artifex MuPDF before 2017-09-25 mishandles a certain case where a variable may reside in a register, which allows remote attackers to cause a denial of service (Fitz fz_drop_imp use-after-free and application crash) or possibly have unspecified other impact via a crafted PDF document.

## References
- http://git.ghostscript.com/?p=mupdf.git%3Bh=c2663e51238ec8256da7fc61ad580db891d9fe9a
- https://bugs.ghostscript.com/show_bug.cgi?id=698592
