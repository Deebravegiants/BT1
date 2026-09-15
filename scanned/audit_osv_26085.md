# [M] CVE-2023-50769

## Summary
Severity: Medium
Advisory: CVE-2023-50769
Aliases: GHSA-4g5f-w3mh-w99m
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-12-13
Source: https://osv.dev/vulnerability/CVE-2023-50769
Type: osv

## Details
Missing permission checks in Jenkins Nexus Platform Plugin 3.18.0-03 and earlier allow attackers with Overall/Read permission to connect to an attacker-specified HTTP server using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

## References
- https://www.jenkins.io/security/advisory/2023-12-13/#SECURITY-3203
- http://www.openwall.com/lists/oss-security/2023/12/13/4
