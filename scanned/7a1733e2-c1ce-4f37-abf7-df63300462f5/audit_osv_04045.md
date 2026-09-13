# [M] Apache Airflow: Config API: team-scoped Celery broker secret disclosed to a Viewer (multi-team masking bypass)

## Summary
Severity: Medium
Advisory: BIT-airflow-2026-65017
Aliases: CVE-2026-65017
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-airflow-2026-65017
Type: osv

## Affected
- Bitnami: `airflow` — affected >=3.3.0 <3.3.1

## Details
Apache Airflow's Config API did not mask team-scoped sensitive configuration values in multi-team deployments. When an administrator has enabled multi-team mode and exposed the Config API, an authenticated Viewer holding only configuration-read access — with no prior access to the secret — could read a team-scoped Celery broker URL, including its embedded credentials, in cleartext, while the equivalent global option was correctly masked. The secrets masker matched only base section and option names and did not normalize team-prefixed sections before the sensitivity check (CWE-200). This is a distinct masker bypass from CVE-2026-48828 and CVE-2026-48892: deployments that upgraded to apache-airflow 3.3.0 to address those issues remain affected by this team-scoped variant. Users are advised to upgrade to apache-airflow 3.3.1 or later, which normalizes team-scoped sections before masking.

## References
- https://github.com/apache/airflow/pull/70755
- https://lists.apache.org/thread/kykn94kjf0tntx4wywtvjowh5bzdgf38
- https://nvd.nist.gov/vuln/detail/CVE-2026-65017
- https://www.cve.org/CVERecord?id=CVE-2026-48828
- https://www.cve.org/CVERecord?id=CVE-2026-48892
