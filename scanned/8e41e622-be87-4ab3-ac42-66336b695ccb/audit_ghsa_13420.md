# [C] Apache Airflow Hive Provider Beeline remote code execution with Principal

## Summary
Severity: Critical
Advisory: GHSA-hg6c-qqcm-r79r
CVE: CVE-2023-35797
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-03
Source: https://github.com/advisories/GHSA-hg6c-qqcm-r79r
Type: github-advisory

## Affected
- PyPI: `apache-airflow-providers-apache-hive` — affected >=0 <6.1.1

## Details
Improper Input Validation vulnerability in Apache Software Foundation Apache Airflow Hive Provider.
This issue affects Apache Airflow Apache Hive Provider: before 6.1.1.

Before version 6.1.1 it was possible to bypass the security check to RCE via
principal parameter. For this to be exploited it requires access to modifying the connection details.

It is recommended updating provider version to 6.1.1 in order to avoid this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-35797
- https://github.com/apache/airflow/pull/31983
- https://github.com/apache/airflow/commit/6724eeb6210d5965937eaf9dae3e476eb30f8268
- https://github.com/apache/airflow
- https://lists.apache.org/thread/30y19ok07fw52x5hnkbhwqo3ho0wwc1y
- http://www.openwall.com/lists/oss-security/2023/07/12/3
