# [M] Apache Atlas: An authenticated user can perform XSS and potentially impersonate another user

## Summary
Severity: Medium
Advisory: GHSA-x3v6-f5fr-4wwv
CVE: CVE-2024-46910
CWE: CWE-80
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2025-02-13
Source: https://github.com/advisories/GHSA-x3v6-f5fr-4wwv
Type: github-advisory

## Affected
- Maven: `org.apache.atlas:apache-atlas` — affected >=2.0.0 <2.4.0

## Details
An authenticated user can perform XSS and potentially impersonate another user.

This issue affects Apache Atlas versions 2.3.0 and earlier.

Users are recommended to upgrade to version 2.4.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-46910
- https://github.com/apache/atlas
- https://lists.apache.org/thread/sqzp34l4cdk21zoq5g31qlsvr7jvb1fy
- http://www.openwall.com/lists/oss-security/2025/02/12/2
