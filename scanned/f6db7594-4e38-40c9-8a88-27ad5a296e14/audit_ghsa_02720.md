# [C] Command Injection in Simiki

## Summary
Severity: Critical
Advisory: GHSA-w873-xcqq-x922
CVE: CVE-2020-19001
CWE: CWE-77
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-01
Source: https://github.com/advisories/GHSA-w873-xcqq-x922
Type: github-advisory

## Affected
- PyPI: `simiki` — affected >=0 <1.6.2.2

## Details
Command Injection in Simiki v1.6.2.1 and prior allows remote attackers to execute arbitrary system commands via line 64 of the component 'simiki/blob/master/simiki/config.py'.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-19001
- https://github.com/tankywoo/simiki/issues/123
- https://github.com/tankywoo/simiki/commit/45da0ab7c1e94b368cac22867e7ac9a42dbb9390
- https://github.com/pypa/advisory-database/tree/main/vulns/simiki/PYSEC-2021-348.yaml
- https://github.com/tankywoo/simiki
