# [M] CVE-2022-43417

## Summary
Severity: Medium
Advisory: CVE-2022-43417
Aliases: GHSA-5fvg-h778-jjjx
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-10-19
Source: https://osv.dev/vulnerability/CVE-2022-43417
Type: osv

## Details
Jenkins Katalon Plugin 1.0.32 and earlier does not perform permission checks in several HTTP endpoints, allowing attackers with Overall/Read permission to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

## References
- http://www.openwall.com/lists/oss-security/2022/10/19/3
- https://www.jenkins.io/security/advisory/2022-10-19/#SECURITY-2845%20%281%29
