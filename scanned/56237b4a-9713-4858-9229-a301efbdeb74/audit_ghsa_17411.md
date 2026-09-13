# [H] Apache StreamPark: Use the user’s password as the secret key Vulnerability

## Summary
Severity: High
Advisory: GHSA-3hg2-rh4r-8qf6
CVE: CVE-2025-53960
CWE: CWE-1240
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-12-12
Source: https://github.com/advisories/GHSA-3hg2-rh4r-8qf6
Type: github-advisory

## Affected
- Maven: `org.apache.streampark:streampark` — affected >=2.0.0 <2.1.7

## Details
When encrypting sensitive data, weak encryption keys that are fixed or directly generated based on user passwords are used. Attackers can obtain these keys through methods such as reverse engineering, code leaks, or password guessing, thereby decrypting stored or transmitted encrypted data, leading to the leakage of sensitive information.

This issue affects Apache StreamPark: from 2.0.0 before 2.1.7.

Users are recommended to upgrade to version 2.1.7, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-53960
- https://github.com/apache/streampark/commit/39034db0c806168afa82e58e4f376e1e3c3b73e4
- https://github.com/apache/streampark
- https://lists.apache.org/thread/xlpvfzf5l5m5mfyjwrz5h4dssm3c32vy
- http://www.openwall.com/lists/oss-security/2025/12/04/1
