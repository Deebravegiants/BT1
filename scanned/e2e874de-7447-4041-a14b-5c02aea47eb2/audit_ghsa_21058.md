# [M] Fava time and filter parameters vulnerable to reflected Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-xrf4-39fm-j5f2
CVE: CVE-2022-2514
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-07-26
Source: https://github.com/advisories/GHSA-xrf4-39fm-j5f2
Type: github-advisory

## Affected
- PyPI: `fava` — affected >=0 <1.22

## Details
The time and filter parameters in Fava prior to v1.22 are vulnerable to reflected cross-site scripting due to the lack of escaping of error messages which contained the parameters in verbatim.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-2514
- https://github.com/beancount/fava/commit/ca9e3882c7b5fbf5273ba52340b9fea6a99f3711
- https://github.com/advisories/GHSA-xrf4-39fm-j5f2
- https://github.com/beancount/fava
- https://github.com/pypa/advisory-database/tree/main/vulns/fava/PYSEC-2022-239.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/fava/PYSEC-2022-43182.yaml
- https://huntr.dev/bounties/dbf77139-4384-4dc5-9994-45a5e0747429
