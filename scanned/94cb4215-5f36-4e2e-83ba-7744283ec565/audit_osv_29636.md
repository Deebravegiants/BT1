# [H] Apache Airflow Fab Provider: Application does not invalidate session after password change via Airflow cli

## Summary
Severity: High
Advisory: CVE-2024-45033
Aliases: GHSA-8863-4qmg-fr45, PYSEC-2026-1147
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-01-08
Source: https://osv.dev/vulnerability/CVE-2024-45033
Type: osv

## Details
Insufficient Session Expiration vulnerability in Apache Airflow Fab Provider.

This issue affects Apache Airflow Fab Provider: before 1.5.2.

When user password has been changed with admin CLI, the sessions for that user have not been cleared, leading to insufficient session expiration, thus logged users could continue to be logged in even after the password was changed. This only happened when the password was changed with CLI. The problem does not happen in case change was done with webserver thus this is different from  CVE-2023-40273 https://github.com/advisories/GHSA-pm87-24wq-r8w9  which was addressed in Apache-Airflow 2.7.0


Users are recommended to upgrade to version 1.5.2, which fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45033.json
- https://lists.apache.org/thread/yw535346rk766ybzpqtvrl36sjj789st
- https://nvd.nist.gov/vuln/detail/CVE-2024-45033
- https://github.com/apache/airflow/pull/45139
- https://pypi.org/project/apache-airflow-providers-fab/
