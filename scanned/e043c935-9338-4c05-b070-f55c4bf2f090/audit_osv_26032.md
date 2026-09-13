# [M] CVE-2023-49653

## Summary
Severity: Medium
Advisory: CVE-2023-49653
Aliases: GHSA-qmhq-876f-cr65
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-11-29
Source: https://osv.dev/vulnerability/CVE-2023-49653
Type: osv

## Details
Jenkins Jira Plugin 3.11 and earlier does not set the appropriate context for credentials lookup, allowing attackers with Item/Configure permission to access and capture credentials they are not entitled to.

## References
- http://www.openwall.com/lists/oss-security/2023/11/29/1
- https://www.jenkins.io/security/advisory/2023-11-29/#SECURITY-3225
