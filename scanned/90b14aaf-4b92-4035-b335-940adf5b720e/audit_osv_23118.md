# [M] CVE-2022-43411

## Summary
Severity: Medium
Advisory: CVE-2022-43411
Aliases: GHSA-f9f9-4r63-4qcc
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-10-19
Source: https://osv.dev/vulnerability/CVE-2022-43411
Type: osv

## Details
Jenkins GitLab Plugin 1.5.35 and earlier uses a non-constant time comparison function when checking whether the provided and expected webhook token are equal, potentially allowing attackers to use statistical methods to obtain a valid webhook token.

## References
- http://www.openwall.com/lists/oss-security/2022/10/19/3
- https://www.jenkins.io/security/advisory/2022-10-19/#SECURITY-2877
