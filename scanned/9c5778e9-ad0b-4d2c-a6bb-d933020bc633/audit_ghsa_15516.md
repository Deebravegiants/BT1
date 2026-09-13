# [M] Apache Answer: Avatar URL leaked user email addresses

## Summary
Severity: Medium
Advisory: GHSA-48cr-j2cx-mcr8
CVE: CVE-2024-40761
CWE: CWE-326
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-09-25
Source: https://github.com/advisories/GHSA-48cr-j2cx-mcr8
Type: github-advisory

## Affected
- Go: `github.com/apache/incubator-answer` — affected >=0 <1.4.0

## Details
Inadequate Encryption Strength vulnerability in Apache Answer.

This issue affects Apache Answer: through 1.3.5.

Using the MD5 value of a user's email to access Gravatar is insecure and can lead to the leakage of user email. The official recommendation is to use SHA256 instead.
Users are recommended to upgrade to version 1.4.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-40761
- https://github.com/apache/incubator-answer/commit/c3a17046c6c3be1cec16ba49d07d9f7742b7260f
- https://github.com/apache/incubator-answer
- https://lists.apache.org/thread/mmrhsfy16qwrw0pkv0p9kj40vy3sg08x
- http://www.openwall.com/lists/oss-security/2024/09/25/2
- http://www.openwall.com/lists/oss-security/2024/09/25/5
- http://www.openwall.com/lists/oss-security/2024/09/25/6
- http://www.openwall.com/lists/oss-security/2024/09/25/7
- http://www.openwall.com/lists/oss-security/2024/09/25/8
- http://www.openwall.com/lists/oss-security/2024/09/26/1
- http://www.openwall.com/lists/oss-security/2024/09/26/3
- http://www.openwall.com/lists/oss-security/2024/09/26/4
- http://www.openwall.com/lists/oss-security/2024/09/27/4
- http://www.openwall.com/lists/oss-security/2024/09/27/5
- http://www.openwall.com/lists/oss-security/2024/09/27/8
