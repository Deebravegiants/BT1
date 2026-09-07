# [M] Cross-site scripting in Contentful

## Summary
Severity: Medium
Advisory: GHSA-g5j6-r3x9-gf2m
CVE: CVE-2020-13258
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-06-18
Source: https://github.com/advisories/GHSA-g5j6-r3x9-gf2m
Type: github-advisory

## Affected
- PyPI: `contentful` — affected >=0 <1.12.4

## Details
Contentful through 2020-05-21 for Python allows reflected XSS, as demonstrated by the api parameter to the-example-app.py.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13258
- https://github.com/contentful/the-example-app.py/issues/44
