# [M] Locust Stored Cross-site Scripting Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-vqxw-9pg7-v7v9
CVE: CVE-2020-28364
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-vqxw-9pg7-v7v9
Type: github-advisory

## Affected
- PyPI: `locust` — affected >=0 <1.3.2

## Details
A stored cross-site scripting (XSS) vulnerability affects the Web UI in Locust before 1.3.2, if the installation violates the usage expectations by exposing this UI to outside users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28364
- https://github.com/locustio/locust/pull/1603
- https://github.com/locustio/locust/commit/0d118179709b4a60174810bae4db41d40e4c99ad
- https://github.com/locustio/locust/commit/4049173b3466da236b1d8d8d3519e73c01525a0d
- https://docs.locust.io/en/stable/changelog.html
- https://github.com/locustio/locust
- https://github.com/pypa/advisory-database/tree/main/vulns/locust/PYSEC-2020-60.yaml
