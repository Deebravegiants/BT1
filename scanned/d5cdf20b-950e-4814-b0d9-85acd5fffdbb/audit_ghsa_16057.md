# [H] Apache Airflow: Sensitive configuration values are not masked in the logs by default

## Summary
Severity: High
Advisory: GHSA-46c3-5xc5-wwhv
CVE: CVE-2024-45784
CWE: CWE-1295
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-11-15
Source: https://github.com/advisories/GHSA-46c3-5xc5-wwhv
Type: github-advisory

## Affected
- PyPI: `airflow` — affected >=0 <2.10.3

## Details
Apache Airflow versions before 2.10.3 contain a vulnerability that could expose sensitive configuration variables in task logs. This vulnerability allows DAG authors to unintentionally or intentionally log sensitive configuration variables. Unauthorized users could access these logs, potentially exposing critical data that could be exploited to compromise the security of the Airflow deployment. In version 2.10.3, secrets are now masked in task logs to prevent sensitive configuration variables from being exposed in the logging output. Users should upgrade to Airflow 2.10.3 or the latest version to eliminate this vulnerability. If you suspect that DAG authors could have logged the secret values to the logs and that your logs are not additionally protected, it is also recommended that you update those secrets.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-45784
- https://github.com/apache/airflow/pull/43040
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2024-182.yaml
- https://lists.apache.org/thread/k2jm55jztlbmk4zrlh10syvq3n57hl4h
- http://www.openwall.com/lists/oss-security/2024/11/15/1
