# [H] CVE-2023-51104

## Summary
Severity: High
Advisory: CVE-2023-51104
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-12-26
Source: https://osv.dev/vulnerability/CVE-2023-51104
Type: osv

## Details
A floating point exception (divide-by-zero) vulnerability was discovered in Artifex MuPDF 1.23.4 in function pnm_binary_read_image() of load-pnm.c when span equals zero.

## References
- http://cgit.ghostscript.com/cgi-bin/cgit.cgi/mupdf.git/commit/?id=0c06a4e51519515615f6ab2d5b1f25da6771e1f4
- https://bugs.ghostscript.com/show_bug.cgi?id=707621
- https://github.com/dongyuma/sox-defects/blob/main/mupdf-defects.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/51xxx/CVE-2023-51104.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-51104
