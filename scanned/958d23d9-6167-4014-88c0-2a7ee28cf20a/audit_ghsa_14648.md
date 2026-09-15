# [H] Apache Superset: Lower privilege users are able to create Role when FAB_ADD_SECURITY_API is enabled

## Summary
Severity: High
Advisory: GHSA-35fc-9hrj-3585
CVE: CVE-2024-53949
CWE: CWE-285, CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-12-09
Source: https://github.com/advisories/GHSA-35fc-9hrj-3585
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=2.0.0 <4.1.0

## Details
Improper Authorization vulnerability in Apache Superset when FAB_ADD_SECURITY_API is enabled (disabled by default). Allows for lower privilege users to use this API.

 issue affects Apache Superset: from 2.0.0 before 4.1.0.

Users are recommended to upgrade to version 4.1.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-53949
- https://github.com/apache/superset/commit/7650c47e72f28559e91524f5d68d50c2060df4c7
- https://github.com/apache/superset
- https://lists.apache.org/thread/d3scbwmfpzbpm6npnzdw5y4owtqqyq8d
- http://www.openwall.com/lists/oss-security/2024/12/09/4
