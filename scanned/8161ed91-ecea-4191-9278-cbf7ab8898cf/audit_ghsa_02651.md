# [M] Cross Site Scripting (XSS) in Simiki

## Summary
Severity: Medium
Advisory: GHSA-fqr5-qphf-vfr8
CVE: CVE-2020-19000
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-09-01
Source: https://github.com/advisories/GHSA-fqr5-qphf-vfr8
Type: github-advisory

## Affected
- PyPI: `simiki` — affected >=0 <1.6.2.2

## Details
Cross Site Scripting (XSS) in Simiki v1.6.2.1 and prior allows remote attackers to execute arbitrary code via line 54 of the component 'simiki/blob/master/simiki/generators.py'.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-19000
- https://github.com/tankywoo/simiki/issues/123
- https://github.com/pypa/advisory-database/tree/main/vulns/simiki/PYSEC-2021-347.yaml
- https://github.com/tankywoo/simiki
