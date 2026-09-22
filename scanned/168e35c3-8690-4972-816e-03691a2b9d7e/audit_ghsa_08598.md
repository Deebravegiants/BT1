# [M] Pillow has a heap buffer overflow with nested list coordinates

## Summary
Severity: Medium
Advisory: GHSA-5xmw-vc9v-4wf2
CVE: CVE-2026-42309
CWE: CWE-122
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-5xmw-vc9v-4wf2
Type: github-advisory

## Affected
- PyPI: `pillow` — affected >=11.2.1 <12.2.0

## Details
Passing nested lists as coordinates to APIs that accept coordinates such as `ImagePath.Path`, `ImageDraw.ImageDraw.polygon` and `ImageDraw.ImageDraw.line` could cause a heap buffer overflow, as nested lists were recursively unpacked beyond the allocated buffer. Coordinate lists are now validated to contain exactly two numeric coordinates. This was introduced in Pillow 11.2.1.

## References
- https://github.com/python-pillow/Pillow/security/advisories/GHSA-5xmw-vc9v-4wf2
- https://nvd.nist.gov/vuln/detail/CVE-2026-42309
- https://github.com/python-pillow/Pillow
- https://github.com/python-pillow/Pillow/releases/tag/12.2.0
