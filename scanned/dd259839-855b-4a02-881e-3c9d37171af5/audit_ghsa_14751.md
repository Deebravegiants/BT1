# [H] luigi Arbitrary File Write via Archive Extraction (Zip Slip)

## Summary
Severity: High
Advisory: GHSA-8qch-vj6m-2694
CVE: CVE-2024-21542
CWE: CWE-22, CWE-29
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2024-12-10
Source: https://github.com/advisories/GHSA-8qch-vj6m-2694
Type: github-advisory

## Affected
- PyPI: `luigi` — affected >=0 <3.6.0

## Details
Versions of the package luigi before 3.6.0 are vulnerable to Arbitrary File Write via Archive Extraction (Zip Slip) due to improper destination file path validation in the _extract_packages_archive function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21542
- https://github.com/spotify/luigi/issues/3301
- https://github.com/spotify/luigi/commit/b5d1b965ead7d9f777a3216369b5baf23ec08999
- https://github.com/pypa/advisory-database/tree/main/vulns/luigi/PYSEC-2024-159.yaml
- https://github.com/spotify/luigi
- https://github.com/spotify/luigi/releases/tag/v3.6.0
- https://security.snyk.io/vuln/SNYK-PYTHON-LUIGI-7830489
