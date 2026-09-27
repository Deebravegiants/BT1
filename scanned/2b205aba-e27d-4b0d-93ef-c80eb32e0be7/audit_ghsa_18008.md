# [M] Apache Superset allows authenticated users to discover metadata about datasources they don't have permission to access

## Summary
Severity: Medium
Advisory: GHSA-mhpq-m962-mg92
CVE: CVE-2025-55675
CWE: CWE-285
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-08-14
Source: https://github.com/advisories/GHSA-mhpq-m962-mg92
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0 <5.0.0

## Details
Apache Superset contains an improper access control vulnerability in its /explore endpoint. A missing authorization check allows an authenticated user to discover metadata about datasources they do not have permission to access. By iterating through the datasource_id in the URL, an attacker can enumerate and confirm the existence and names of protected datasources, leading to sensitive information disclosure.

This issue affects Apache Superset: before 5.0.0.

Users are recommended to upgrade to version 5.0.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-55675
- https://github.com/apache/superset
- https://lists.apache.org/thread/op681b4kbd7g84tfjf9omz0sxggbcv33
- http://www.openwall.com/lists/oss-security/2025/08/14/6
