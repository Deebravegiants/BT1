# [H] Kotti CSRF in the local roles implementation

## Summary
Severity: High
Advisory: GHSA-3hq4-f2v6-q338
CVE: CVE-2018-9856
CWE: CWE-352
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-07-12
Source: https://github.com/advisories/GHSA-3hq4-f2v6-q338
Type: github-advisory

## Affected
- PyPI: `Kotti` — affected >=0 <1.3.2
- PyPI: `Kotti` — affected >=2.0.0a1 <2.0.0b2

## Details
Kotti before 1.3.2 and 2.x before 2.0.0b2 has CSRF in the local roles implementation, as demonstrated by triggering a permission change via a `/admin-document/@@share` request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-9856
- https://github.com/Kotti/Kotti/issues/551
- https://github.com/Kotti/Kotti/commit/69d3c8a5d7203ddaec5ced5901acf87baddd76be
- https://github.com/Kotti/Kotti
- https://github.com/advisories/GHSA-3hq4-f2v6-q338
- https://github.com/pypa/advisory-database/tree/main/vulns/kotti/PYSEC-2018-10.yaml
