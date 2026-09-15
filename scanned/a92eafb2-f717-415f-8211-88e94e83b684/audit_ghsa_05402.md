# [M] Apache StreamPipes has Improper Privilege Management issue

## Summary
Severity: Medium
Advisory: GHSA-5r2g-vphf-m5xc
CVE: CVE-2025-47411
CWE: CWE-269
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-01-01
Source: https://github.com/advisories/GHSA-5r2g-vphf-m5xc
Type: github-advisory

## Affected
- Maven: `org.apache.streampipes:streampipes-parent` — affected >=0.69.0 <0.98.0

## Details
A user with a legitimate non-administrator account can exploit a vulnerability in the user ID creation mechanism in Apache StreamPipes that allows them to swap the username of an existing user with that of an administrator. 

This vulnerability allows an attacker to gain administrative control over the application by manipulating JWT tokens, which can lead to data tampering, unauthorized access and other security issues.

This issue affects Apache StreamPipes: through 0.97.0.

Users are recommended to upgrade to version 0.98.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-47411
- https://github.com/apache/streampipes
- https://github.com/apache/streampipes/releases/tag/release%2F0.98.0
- https://lists.apache.org/thread/lngko4ht2ok3o0rk9h0clgm4kb0lmt36
- http://www.openwall.com/lists/oss-security/2025/12/29/14
