# [M] CVE-2021-21637

## Summary
Severity: Medium
Advisory: CVE-2021-21637
Aliases: GHSA-6364-jx4h-7564
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-03-30
Source: https://osv.dev/vulnerability/CVE-2021-21637
Type: osv

## Details
A missing permission check in Jenkins Team Foundation Server Plugin 5.157.1 and earlier allows attackers with Overall/Read permission to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

## References
- http://www.openwall.com/lists/oss-security/2021/03/30/1
- https://www.jenkins.io/security/advisory/2021-03-30/#SECURITY-2283%20%282%29
