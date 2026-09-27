# [H] libheif: heap OOB read in ImageItem_Grid::decode_grid_tile via irot-induced tile-coordinate underflow

## Summary
Severity: High
Advisory: CVE-2026-48029
Aliases: GHSA-6x5f-qchq-cxqv
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2026-07-22
Source: https://osv.dev/vulnerability/CVE-2026-48029
Type: osv

## Details
libheif is a HEIF and AVIF file format decoder and encoder. Versions 1.19.0 through 1.21.2 have a heap OOB read in ImageItem_Grid::decode_grid_tile via irot-induced tile-coordinate underflow. Version 1.22.0 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48029.json
- https://github.com/strukturag/libheif/security/advisories/GHSA-6x5f-qchq-cxqv
- https://nvd.nist.gov/vuln/detail/CVE-2026-48029
- https://github.com/strukturag/libheif/commit/e523ec0bf379110b7c33d4c159f8b1202d332157
