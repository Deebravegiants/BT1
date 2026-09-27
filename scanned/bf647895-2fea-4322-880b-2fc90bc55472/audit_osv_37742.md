# [H] CVE-2026-3308

## Summary
Severity: High
Advisory: CVE-2026-3308
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/CVE-2026-3308
Type: osv

## Details
An integer overflow vulnerability in 'pdf-image.c' in Artifex's MuPDF version 1.27.0 allows an attacker to maliciously craft a PDF that can trigger an integer overflow within the 'pdf_load_image_imp' function. This allows a heap out-of-bounds write that could be exploited for arbitrary code execution.

## References
- https://cgit.ghostscript.com/cgi-bin/cgit.cgi/mupdf.git/commit/?id=a26f0142e7d390d4a82c6e5ae0e312e07cc4ec85
- https://lists.debian.org/debian-lts-announce/2026/04/msg00020.html
- https://www.kb.cert.org/vuls/id/951662
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/3xxx/CVE-2026-3308.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-3308
- https://github.com/ArtifexSoftware/mupdf/commit/a26f0142e7d390d4a82c6e5ae0e312e07cc4ec85
- https://github.com/ArtifexSoftware/mupdf
