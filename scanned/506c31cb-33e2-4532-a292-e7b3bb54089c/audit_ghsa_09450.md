# [M] Pillow has an integer overflow when processing fonts

## Summary
Severity: Medium
Advisory: GHSA-wjx4-4jcj-g98j
CVE: CVE-2026-42308
CWE: CWE-190
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-wjx4-4jcj-g98j
Type: github-advisory

## Affected
- PyPI: `pillow` — affected >=0 <12.2.0

## Details
If a font advances for each glyph by an exceeding large amount, when Pillow keeps track of the current position, it may lead to an integer overflow. This has been fixed.

## References
- https://github.com/python-pillow/Pillow/security/advisories/GHSA-wjx4-4jcj-g98j
- https://nvd.nist.gov/vuln/detail/CVE-2026-42308
- https://github.com/pypa/advisory-database/tree/main/vulns/pillow/PYSEC-2026-165.yaml
- https://github.com/python-pillow/Pillow
- https://github.com/python-pillow/Pillow/releases/tag/12.2.0
