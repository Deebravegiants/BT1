# [H] Airflow Sqoop Provider RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-g3m9-pr5m-4cvp
CVE: CVE-2023-27604
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-08-28
Source: https://github.com/advisories/GHSA-g3m9-pr5m-4cvp
Type: github-advisory

## Affected
- PyPI: `apache-airflow-providers-apache-sqoop` — affected >=0 <4.0.0

## Details
Apache Airflow Sqoop Provider, versions before 4.0.0, is affected by a vulnerability that allows an attacker pass parameters with the connections, which makes it possible to implement RCE attacks via ‘sqoop import --connect’, obtain airflow server permissions, etc. The attacker needs to be logged in and have authorization (permissions) to create/edit connections.

 It is recommended to upgrade to a version that is not affected.
This issue was reported independently by happyhacking-k, And Xie Jianming and LiuHui of Caiji Sec Team also reported it.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-27604
- https://github.com/apache/airflow/pull/33039
- https://github.com/apache/airflow
- https://lists.apache.org/thread/lswlxf11do51ob7f6xyyg8qp3n7wdrgd
