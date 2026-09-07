# [C] Apache Airflow vulnerable to XSS

## Summary
Severity: Critical
Advisory: GHSA-9gqg-3fxr-9hv7
CVE: CVE-2017-17836
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-01-25
Source: https://github.com/advisories/GHSA-9gqg-3fxr-9hv7
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <1.9.0

## Details
In Apache Airflow 1.8.2 and earlier, an experimental Airflow feature displayed authenticated cookies, as well as passwords to databases used by Airflow. An attacker who has limited access to airflow, weather it be via XSS or by leaving a machine unlocked can exfil all credentials from the system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-17836
- https://github.com/advisories/GHSA-9gqg-3fxr-9hv7
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2019-149.yaml
- https://lists.apache.org/thread.html/ade4d54ebf614f68dc81a08891755e60ea58ba88e0209233eeea5f57@%3Cdev.airflow.apache.org%3E
