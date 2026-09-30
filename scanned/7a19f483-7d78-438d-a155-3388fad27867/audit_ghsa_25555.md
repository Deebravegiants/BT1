# [C] SQL injection in apache-superset

## Summary
Severity: Critical
Advisory: GHSA-wh73-hpcg-v32j
CVE: CVE-2022-27479
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-14
Source: https://github.com/advisories/GHSA-wh73-hpcg-v32j
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0 <1.4.2

## Details
Apache Superset before 1.4.2 is vulnerable to SQL injection in chart data requests. Users should update to 1.4.2 or higher which addresses this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-27479
- https://github.com/advisories/GHSA-wh73-hpcg-v32j
- https://github.com/apache/superset
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-superset/PYSEC-2022-188.yaml
- https://lists.apache.org/thread/94th50j5d0y2fw7ysx0g7w3t6jk3z7q6
- https://lists.apache.org/thread/ztb9b6jd9rngoxwvq8r4fhpp401o613y
- http://www.openwall.com/lists/oss-security/2022/04/13/3
