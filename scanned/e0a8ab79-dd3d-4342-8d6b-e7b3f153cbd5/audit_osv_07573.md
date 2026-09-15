# [C] Apache Superset: Improper SQL authorisation, parse not checking for specific postgres functions

## Summary
Severity: Critical
Advisory: BIT-superset-2024-53947
Aliases: CVE-2024-53947, GHSA-92qf-8gh3-gwcm, PYSEC-2026-1165
Ecosystem: Bitnami
Published: 2025-04-14
Source: https://osv.dev/vulnerability/BIT-superset-2024-53947
Type: osv

## Affected
- Bitnami: `superset` — affected >=0 <4.1.1

## Details
Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection') vulnerability in Apache Superset. Specifically, certain engine-specific functions are not checked, which allows attackers to bypass Apache Superset's SQL authorization. This issue is a follow-up to CVE-2024-39887 with additional disallowed PostgreSQL functions now included: query_to_xml_and_xmlschema, table_to_xml, table_to_xml_and_xmlschema.

This issue affects Apache Superset: <4.1.0.

Users are recommended to upgrade to version 4.1.0, which fixes the issue or add these Postgres functions to the config set DISALLOWED_SQL_FUNCTIONS.

## References
- https://lists.apache.org/thread/hj3gfsjh67vqw12nlrshlsym4bkopjmn
- https://nvd.nist.gov/vuln/detail/CVE-2024-53947
