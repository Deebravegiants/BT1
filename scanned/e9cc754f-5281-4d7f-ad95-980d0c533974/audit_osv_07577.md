# [M] Apache Superset: Regular Expression Denial of Service (ReDoS) in SQL Parser

## Summary
Severity: Medium
Advisory: BIT-superset-2026-23985
Aliases: CVE-2026-23985
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-superset-2026-23985
Type: osv

## Affected
- Bitnami: `superset` — affected >=0 <6.0.0

## Details
A Regular Expression Denial of Service (ReDoS) vulnerability exists in Apache Superset versions 1.5.0 through 5.0.0. The vulnerability is located in the sql_parse.py component, specifically within the SQL_REGEX used for parsing SQL statements in the sqlparse library integration.
The affected regular expression contains overlapping disjunctions that share a common outer quantifier. An authenticated attacker can exploit this by sending a maliciously crafted input string (specifically a long sequence of backslashes or similar characters) to endpoints that process SQL queries

This issue affects Apache Superset: before 6.0.0.

Users are recommended to upgrade to version 6.0.0, which fixes the issue. 

Workarounds:
● WAF Rules: Implement Web Application Firewall (WAF) rules to detect and block
requests containing excessively long sequences of backslashes or suspicious repeated
patterns in the queries.extras.where parameter.
● Rate Limiting: Ensure strict rate limiting is applied to the /api/v1/chart/data endpoint to
reduce the impact of potential attacks.

## References
- http://www.openwall.com/lists/oss-security/2026/07/30/7
- https://lists.apache.org/thread/fdy7tx7glv90ypd7qnm1g1pt7nn336qx
- https://nvd.nist.gov/vuln/detail/CVE-2026-23985
