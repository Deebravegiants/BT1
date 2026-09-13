# [C] Apache Airflow: JWT token still valid after logout

## Summary
Severity: Critical
Advisory: GHSA-c92r-g8j5-vhcx
CVE: CVE-2025-57735
CWE: CWE-613
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-c92r-g8j5-vhcx
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=3.0.0 <3.2.0

## Details
When user logged out, the JWT token the user had authtenticated with was not invalidated, which could lead to reuse of that token in case it was intercepted. In Airflow 3.2 we implemented the mechanism that implements token invalidation at logout. Users who are concerned about the logout scenario and possibility of intercepting the tokens, should upgrade to Airflow 3.2+



Users are recommended to upgrade to version 3.2.0, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-57735
- https://github.com/apache/airflow/pull/56633
- https://github.com/apache/airflow/pull/61339
- https://github.com/apache/airflow
- https://lists.apache.org/thread/ovn8mpd8zkc604hojt7x3wsw3kc60x98
- http://www.openwall.com/lists/oss-security/2026/04/09/16
