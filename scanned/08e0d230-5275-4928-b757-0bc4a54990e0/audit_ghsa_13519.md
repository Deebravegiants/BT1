# [H] Apache Airflow Celery provider Insertion of Sensitive Information into Log File vulnerability

## Summary
Severity: High
Advisory: GHSA-666g-rfc5-c9jv
CVE: CVE-2023-46215
CWE: CWE-532
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-10-28
Source: https://github.com/advisories/GHSA-666g-rfc5-c9jv
Type: github-advisory

## Affected
- PyPI: `apache-airflow-providers-celery` — affected >=3.3.0 <3.4.1
- PyPI: `apache-airflow` — affected >=1.10.0 <2.7.0

## Details
Insertion of Sensitive Information into Log File vulnerability in Apache Airflow Celery provider, Apache Airflow.

Sensitive information logged as clear text when rediss, amqp, rpc protocols are used as Celery result backend
Note: the vulnerability is about the information exposed in the logs not about accessing the logs.

This issue affects Apache Airflow Celery provider: from 3.3.0 through 3.4.0; Apache Airflow: from 1.10.0 through 2.6.3.

Users are recommended to upgrade Airflow Celery provider to version 3.4.1 and Apache Airlfow to version 2.7.0 which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-46215
- https://github.com/apache/airflow/pull/34954
- https://github.com/apache/airflow
- https://lists.apache.org/thread/wm1jfmks7r6m7bj0mq4lmw3998svn46n
- http://www.openwall.com/lists/oss-security/2023/10/28/1
