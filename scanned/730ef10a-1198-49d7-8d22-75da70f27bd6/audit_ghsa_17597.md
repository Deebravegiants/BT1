# [C] Apache Airflow Providers Snowflake package allows for Special Element Injection via CopyFromExternalStageToSnowflakeOperator

## Summary
Severity: Critical
Advisory: GHSA-9r64-3wmc-x8m8
CVE: CVE-2025-50213
CWE: CWE-75
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-06-26
Source: https://github.com/advisories/GHSA-9r64-3wmc-x8m8
Type: github-advisory

## Affected
- PyPI: `apache-airflow-providers-snowflake` — affected >=0 <6.4.0

## Details
Failure to Sanitize Special Elements into a Different Plane (Special Element Injection) vulnerability in Apache Airflow Providers Snowflake.

This issue affects Apache Airflow Providers Snowflake: before 6.4.0.

Sanitation of table and stage parameters were added in CopyFromExternalStageToSnowflakeOperator to prevent SQL injection
Users are recommended to upgrade to version 6.4.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-50213
- https://github.com/apache/airflow/pull/51734
- https://github.com/apache/airflow/pull/51734/commits/bcf19916738e4a7065a3911814ba1fa32d6fd669
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow-providers-snowflake/PYSEC-2025-51.yaml
- https://lists.apache.org/thread/2kqfmyt2pghg5f6797g8hzvq331v8qx3
