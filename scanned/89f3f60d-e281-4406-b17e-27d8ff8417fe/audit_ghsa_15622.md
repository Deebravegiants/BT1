# [M] Apache Superset vulnerable to improper SQL authorization

## Summary
Severity: Medium
Advisory: GHSA-2q6j-vpvr-6pvj
CVE: CVE-2024-39887
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-07-16
Source: https://github.com/advisories/GHSA-2q6j-vpvr-6pvj
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0 <4.0.2

## Details
An SQL Injection vulnerability in Apache Superset exists due to improper neutralization of special elements used in SQL commands. Specifically, certain engine-specific functions are not checked, which allows attackers to bypass Apache Superset's SQL authorization. To mitigate this, a new configuration key named DISALLOWED_SQL_FUNCTIONS has been introduced. This key disallows the use of the following PostgreSQL functions: version, query_to_xml, inet_server_addr, and inet_client_addr. Additional functions can be added to this list for increased protection.

This issue affects Apache Superset: before 4.0.2.

Users are recommended to upgrade to version 4.0.2, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-39887
- https://github.com/apache/superset/commit/56f0103b5771d477dd106272abbd8021c9ea7506
- https://github.com/apache/superset
- https://lists.apache.org/thread/j55vm41jg3l0x6w49zrmvbf3k0ts5fqz
- http://www.openwall.com/lists/oss-security/2024/07/16/5
