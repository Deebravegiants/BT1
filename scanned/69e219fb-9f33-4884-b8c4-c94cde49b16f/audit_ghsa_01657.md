# [M] Information disclosure in Apache Superset

## Summary
Severity: Medium
Advisory: GHSA-fxjm-wvj9-9c39
CVE: CVE-2020-1932
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-02-26
Source: https://github.com/advisories/GHSA-fxjm-wvj9-9c39
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0.34.0 <0.35.2

## Details
An information disclosure issue was found in Apache Superset 0.34.0, 0.34.1, 0.35.0, and 0.35.1. Authenticated Apache Superset users are able to retrieve other users' information, including hashed passwords, by accessing an unused and undocumented API endpoint on Apache Superset.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1932
- https://github.com/apache/superset
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-superset/PYSEC-2020-224.yaml
- https://lists.apache.org/thread.html/r4e5323c3bc786005495311a6ff53ac6d990b2c7eb52941a1a13ce227%40%3Cdev.superset.apache.org%3E
