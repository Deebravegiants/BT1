# [C] Command injection in Gerapy

## Summary
Severity: Critical
Advisory: GHSA-g57j-q48p-9vm2
CVE: CVE-2020-7698
CWE: CWE-74
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-g57j-q48p-9vm2
Type: github-advisory

## Affected
- PyPI: `gerapy` — affected >=0 <0.9.3

## Details
This affects the package Gerapy from 0 and before 0.9.3. The input being passed to Popen, via the project_configure endpoint, isn’t being sanitized.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7698
- https://github.com/Gerapy/Gerapy/commit/e8446605eb2424717418eae199ec7aad573da2d2
- https://github.com/Gerapy/Gerapy
- https://github.com/advisories/GHSA-g57j-q48p-9vm2
- https://github.com/pypa/advisory-database/tree/main/vulns/gerapy/PYSEC-2020-44.yaml
- https://snyk.io/vuln/SNYK-PYTHON-GERAPY-572470
