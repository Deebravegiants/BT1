# [M] CImg Library: Uncontrolled memory allocation via nb_colors field in _load_bmp

## Summary
Severity: Medium
Advisory: CVE-2026-42146
Aliases: GHSA-g54r-qmgx-c6fv
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/CVE-2026-42146
Type: osv

## Details
CImg Library is a C++ library for image processing. Prior to commit c3aacf5, the nb_colors field read from the BMP file header is used directly to compute an allocation size without validating it against the remaining file size. A crafted BMP file with a large nb_colors value triggers an out-of-memory condition, crashing any application that uses CImg to load untrusted BMP files. This issue has been patched via commit c3aacf5.

## References
- https://github.com/GreycLab/CImg/releases/tag/v.3.7.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42146.json
- https://github.com/GreycLab/CImg/security/advisories/GHSA-g54r-qmgx-c6fv
- https://nvd.nist.gov/vuln/detail/CVE-2026-42146
- https://github.com/GreycLab/CImg/issues/477
- https://github.com/GreycLab/CImg/commit/c3aacf5b96ac1e54b7af1957c6737dbf3949f6d3
