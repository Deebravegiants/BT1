# [M] Apache Airflow exposes sensitive information in its log files

## Summary
Severity: Medium
Advisory: GHSA-8r55-rv5w-6pfm
CVE: CVE-2025-27555
CWE: CWE-201, CWE-532
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-02-24
Source: https://github.com/advisories/GHSA-8r55-rv5w-6pfm
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <2.11.1

## Details
Airflow versions before 2.11.1 have a vulnerability that allows authenticated users with audit log access to see sensitive values in audit logs which they should not see. When sensitive connection parameters were set via airflow CLI, values of those variables appeared in the audit log and were stored unencrypted in the Airflow database. While this risk is limited to users with audit log access, it is recommended to upgrade to Airflow 2.11.1 or a later version, which addresses this issue. Users who previously used the CLI to set connections should manually delete entries with those connection sensitive values from the log table. This is similar but not the same issue as CVE-2024-50378

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-27555
- https://github.com/apache/airflow/pull/61882
- https://github.com/apache/airflow
- https://lists.apache.org/thread/nxovkp319jo8vg498gql1yswtb2frbkw
