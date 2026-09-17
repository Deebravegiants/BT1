# [H] opencv-contrib-python bundled libwebp binaries in wheels that are vulnerable to CVE-2023-4863

## Summary
Severity: High
Advisory: GHSA-cxjf-x6jp-p7mc
CWE: CWE-787
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-08-30
Source: https://github.com/advisories/GHSA-cxjf-x6jp-p7mc
Type: github-advisory

## Affected
- PyPI: `opencv-contrib-python` — affected >=0 <4.8.1.78

## Details
opencv-contrib-python versions before v4.8.1.78 bundled libwebp binaries in wheels that are vulnerable to CVE-2023-4863. opencv-contrib-python v4.8.1.78 upgrades the bundled libwebp binary to v1.3.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-4863
- https://github.com/opencv/opencv/pull/24274
- https://github.com/opencv/opencv/commit/687fc11626901cff09d2b3b5f331fd59190ad4c7
- https://github.com/advisories/GHSA-j7hp-h8jx-5ppr
- https://github.com/opencv/opencv-python
- https://github.com/opencv/opencv/wiki/ChangeLog#version481
- https://github.com/pypa/advisory-database/tree/main/vulns/opencv-contrib-python/PYSEC-2023-181.yaml
