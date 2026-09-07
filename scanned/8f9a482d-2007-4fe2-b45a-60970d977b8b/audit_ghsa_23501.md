# [H] Apache Superset SQL Injection when template processing is enabled

## Summary
Severity: High
Advisory: GHSA-pg8m-4p8j-2p56
CVE: CVE-2021-41971
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-pg8m-4p8j-2p56
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0 <1.3.1

## Details
Apache Superset up to and including 1.3.0 when configured with ENABLE_TEMPLATE_PROCESSING on (disabled by default) allowed SQL injection when a malicious authenticated user sends an http request with a custom URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-41971
- https://github.com/advisories/GHSA-pg8m-4p8j-2p56
- https://github.com/apache/superset
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-superset/PYSEC-2021-378.yaml
- https://lists.apache.org/thread.html/rf7292731268c6c6e2196ae1583e32ac7189385364268f8d9215e8e6d%40%3Cdev.superset.apache.org%3E
