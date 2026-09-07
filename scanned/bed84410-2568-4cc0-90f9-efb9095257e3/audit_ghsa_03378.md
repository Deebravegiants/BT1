# [M] LinkedIn Oncall vulnerable to Cross-Site Scripting

## Summary
Severity: Medium
Advisory: GHSA-rfw2-x9f8-2f6m
CVE: CVE-2021-26722
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-04-30
Source: https://github.com/advisories/GHSA-rfw2-x9f8-2f6m
Type: github-advisory

## Affected
- PyPI: `oncall` — affected >=0 <1.4.1

## Details
LinkedIn Oncall through 1.4.0 allows reflected XSS via /query because of mishandling of the "No results found for" message in the search bar.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-26722
- https://github.com/linkedin/oncall/issues/341
- https://github.com/linkedin/oncall/commit/843bc106a1c1b1699e9e52b6b0d01c7efe1d6225
- https://github.com/advisories/GHSA-rfw2-x9f8-2f6m
- https://github.com/linkedin/oncall
- https://github.com/pypa/advisory-database/tree/main/vulns/oncall/PYSEC-2021-33.yaml
- https://pypi.org/project/oncall
