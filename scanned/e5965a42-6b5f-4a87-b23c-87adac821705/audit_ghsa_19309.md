# [M] Apache Superset Allows Ownership Takeover

## Summary
Severity: Medium
Advisory: GHSA-w6c7-j32f-rq8j
CVE: CVE-2025-27696
CWE: CWE-285, CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-05-13
Source: https://github.com/advisories/GHSA-w6c7-j32f-rq8j
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0 <4.1.2

## Details
Improper Authorization vulnerability in Apache Superset allows ownership takeover of dashboards, charts or datasets by authenticated users with read permissions.

This issue affects Apache Superset: through 4.1.1.

Users are recommended to upgrade to version 4.1.2 or above, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-27696
- https://github.com/apache/superset/commit/fc844d3dfdace890b32c00a507a959b81122b425
- https://github.com/apache/superset
- https://lists.apache.org/thread/k2od03bxnxs6vcp80sr03ywcxl194413
- http://www.openwall.com/lists/oss-security/2025/05/12/3
