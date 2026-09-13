# [H] Apache Superset: Read-Only Bypass via Improper Input Validation on PostgreSQL Connections

## Summary
Severity: High
Advisory: GHSA-mwf2-qr4v-94h2
CVE: CVE-2026-23984
CWE: CWE-200, CWE-863
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-24
Source: https://github.com/advisories/GHSA-mwf2-qr4v-94h2
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0 <6.0.0

## Details
An Improper Input Validation vulnerability exists in Apache Superset that allows an authenticated user with SQLLab access to bypass the read-only verification check when using a PostgreSQL database connection.
While the system effectively blocks standard Data Manipulation Language (DML) statements (e.g., INSERT, UPDATE, DELETE) on read-only connections, it fails to detect them in specially crafted SQL statements.

This issue affects Apache Superset: before 6.0.0.

Users are recommended to upgrade to version 6.0.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-23984
- https://github.com/apache/superset
- https://lists.apache.org/thread/72cmgxtvp9pclto4ln1chbs1227nwd26
- http://www.openwall.com/lists/oss-security/2026/02/24/8
