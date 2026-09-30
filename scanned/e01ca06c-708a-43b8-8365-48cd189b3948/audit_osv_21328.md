# [M] CVE-2021-4216

## Summary
Severity: Medium
Advisory: CVE-2021-4216
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-08-26
Source: https://osv.dev/vulnerability/CVE-2021-4216
Type: osv

## Details
A Floating point exception (division-by-zero) flaw was found in Mupdf for zero width pages in muraster.c. It is fixed in Mupdf-1.20.0-rc1 upstream.

## References
- https://bugs.ghostscript.com/show_bug.cgi?id=704834
- https://github.com/ArtifexSoftware/mupdf/commit/22c47acbd52949421f8c7cb46ea1556827d0fcbf
