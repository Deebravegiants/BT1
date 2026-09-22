# [M] Apache Airflow: Cache Control - Storage of Sensitive Data in Browser Cache

## Summary
Severity: Medium
Advisory: BIT-airflow-2024-25142
Aliases: CVE-2024-25142, GHSA-9xpj-62mm-24h2, PYSEC-2024-195
Ecosystem: Bitnami
Published: 2024-06-18
Source: https://osv.dev/vulnerability/BIT-airflow-2024-25142
Type: osv

## Affected
- Bitnami: `airflow` — affected >=0 <2.9.2

## Details
Use of Web Browser Cache Containing Sensitive Information vulnerability in Apache Airflow. 

Airflow did not return "Cache-Control" header for dynamic content, which in case of some browsers could result in potentially storing sensitive data in local cache of the browser.

This issue affects Apache Airflow: before 2.9.2.

Users are recommended to upgrade to version 2.9.2, which fixes the issue.

## References
- https://github.com/apache/airflow/pull/39550
- https://lists.apache.org/thread/cg1j28lk0fhzthk0of1g7vy7p2n1j7nr
- http://www.openwall.com/lists/oss-security/2024/06/13/1
- https://nvd.nist.gov/vuln/detail/CVE-2024-25142
