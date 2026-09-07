# [M] Apache Airflow: Secrets from Airflow config file logged in plain text in DAG run logs UI

## Summary
Severity: Medium
Advisory: GHSA-j86x-fwp2-qh7v
CVE: CVE-2025-66236
CWE: CWE-532
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-13
Source: https://github.com/advisories/GHSA-j86x-fwp2-qh7v
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=3.0.0 <3.2.0

## Details
Before Airflow 3.2.0, it was unclear that secure Airflow deployments require the Deployment Manager to take appropriate actions and pay attention to security details and security model of Airflow. Some assumptions the Deployment Manager could make were not clear or explicit enough, even though Airflow's intentions and security model of Airflow did not suggest different assumptions. The overall security model, workload isolation, and JWT authentication details are now described in more detail. Users concerned with role isolation and following the Airflow security model of Airflow are advised to upgrade to Airflow 3.2, where several security improvements have been implemented. They should also read and follow the relevant documents to make sure that their deployment is secure enough. It also clarifies that the Deployment Manager is ultimately responsible for securing your Airflow deployment. This had also been communicated via Airflow 3.2.0 Blog announcement.

Users are recommended to upgrade to version 3.2.0, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-66236
- https://github.com/apache/airflow/pull/58662
- https://airflow.apache.org/blog/airflow-3.2.0
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2026-8.yaml
- https://lists.apache.org/thread/g8fyy1tkmxkkfk7tx2v6h8mvwzpyykbo
- http://www.openwall.com/lists/oss-security/2026/04/13/6
