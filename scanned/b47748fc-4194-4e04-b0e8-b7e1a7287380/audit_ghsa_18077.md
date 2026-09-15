# [M] Apache Superset data query improperly discloses database schema information to low-privileged guest user

## Summary
Severity: Medium
Advisory: GHSA-9g5x-mm39-wg9r
CVE: CVE-2025-55673
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-08-14
Source: https://github.com/advisories/GHSA-9g5x-mm39-wg9r
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0 <4.1.3.post1

## Details
When a guest user accesses a chart in Apache Superset, the API response from the /chart/data endpoint includes a query field in its payload. This field contains the underlying query, which improperly discloses database schema information, such as table names, to the low-privileged guest user.

This issue affects Apache Superset: before 4.1.3.

Users are recommended to upgrade to version 4.1.3, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-55673
- https://github.com/apache/superset
- https://lists.apache.org/thread/h2hw756wk4sj4z49blvzkr5fntl9hlf8
- http://www.openwall.com/lists/oss-security/2025/08/14/3
