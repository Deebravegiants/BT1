# [M] Apache Superset has incorrect authorization check

## Summary
Severity: Medium
Advisory: GHSA-95ch-p3gw-23qg
CVE: CVE-2023-32672
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-09-06
Source: https://github.com/advisories/GHSA-95ch-p3gw-23qg
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0

## Details
An Incorrect authorisation check in SQLLab in Apache Superset versions up to and including 2.1.0. This vulnerability allows an authenticated user to query tables that they do not have proper access to within Superset. The vulnerability can be exploited by leveraging a SQL parsing vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-32672
- https://github.com/apache/superset
- https://lists.apache.org/thread/ococ6nlj80f0okkwfwpjczy3q84j3wkp
