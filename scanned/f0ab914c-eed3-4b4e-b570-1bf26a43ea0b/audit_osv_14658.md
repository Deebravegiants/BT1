# [M] CVE-2019-10438

## Summary
Severity: Medium
Advisory: CVE-2019-10438
Aliases: GHSA-jww4-2793-9gmg
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-10-16
Source: https://osv.dev/vulnerability/CVE-2019-10438
Type: osv

## Details
A missing permission check in Jenkins CRX Content Package Deployer Plugin 1.8.1 and earlier allowed attackers with Overall/Read permission to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

## References
- https://jenkins.io/security/advisory/2019-10-16/#SECURITY-1006%20%281%29
