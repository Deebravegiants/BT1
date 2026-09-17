# [H] Apache StreamPark has a hard-coded encryption key

## Summary
Severity: High
Advisory: GHSA-prv5-c2px-j9q3
CVE: CVE-2025-54947
CWE: CWE-321, CWE-798
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-12-12
Source: https://github.com/advisories/GHSA-prv5-c2px-j9q3
Type: github-advisory

## Affected
- Maven: `org.apache.streampark:streampark` — affected >=2.0.0 <2.1.7

## Details
In Apache StreamPark versions 2.0.0 through 2.1.7, a security vulnerability involving a hard-coded encryption key exists. This vulnerability occurs because the system uses a fixed, immutable key for encryption instead of dynamically generating or securely configuring the key. Attackers may obtain this key through reverse engineering or code analysis, potentially decrypting sensitive data or forging encrypted information, leading to information disclosure or unauthorized system access.

This issue affects Apache StreamPark: from 2.0.0 before 2.1.7.

Users are recommended to upgrade to version 2.1.7, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-54947
- https://github.com/apache/streampark/commit/39034db0c806168afa82e58e4f376e1e3c3b73e4
- https://github.com/apache/streampark
- https://lists.apache.org/thread/kdntmzyzrco75x9q6mc6s8lty1fxmog1
- http://www.openwall.com/lists/oss-security/2025/12/12/3
