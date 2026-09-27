# [M] Apache Airflow exposes secret values to authenticated UI users via rendered templates

## Summary
Severity: Medium
Advisory: GHSA-fv47-pqh6-wxgq
CVE: CVE-2025-66388
CWE: CWE-201
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-12-15
Source: https://github.com/advisories/GHSA-fv47-pqh6-wxgq
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=3.1.0 <3.1.5

## Details
A vulnerability in Apache Airflow allowed authenticated UI users to view secret values in rendered templates due to secrets not being properly redacted, potentially exposing secrets to users without the appropriate authorization.

Users are recommended to upgrade to version 3.1.4, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-66388
- https://github.com/apache/airflow/pull/58767
- https://github.com/apache/airflow/pull/58772
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2025-86.yaml
- https://lists.apache.org/thread/mv9hzsx8grjf7gdlkxwppnpbtogtls2g
- http://www.openwall.com/lists/oss-security/2025/12/12/1
