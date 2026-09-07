# [H] Cross-Site Request Forgery (CSRF) in Apache Airflow

## Summary
Severity: High
Advisory: GHSA-68wv-rjrm-576p
CVE: CVE-2017-17835
CWE: CWE-352
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-01-25
Source: https://github.com/advisories/GHSA-68wv-rjrm-576p
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <1.9.0

## Details
In Apache Airflow 1.8.2 and earlier, a CSRF vulnerability allowed for a remote command injection on a default install of Airflow.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-17835
- https://github.com/apache/airflow/commit/673026c740411cc6447aede8c6a816460fe03a59
- https://github.com/apache/airflow/commit/6aca2c2d395952341ab1b201c59011920b5a5c77
- https://github.com/apache/airflow/commit/c9dc9263986c1a55520ba44b6e5b0fcbd6c48712
- https://github.com/apache/airflow/commit/dca5e7d116b5c8b103df13f89f061757c13c41ae
- https://github.com/advisories/GHSA-68wv-rjrm-576p
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2019-148.yaml
- https://lists.apache.org/thread.html/ade4d54ebf614f68dc81a08891755e60ea58ba88e0209233eeea5f57@%3Cdev.airflow.apache.org%3E
