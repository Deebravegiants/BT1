# [M] CVE-2022-41254

## Summary
Severity: Medium
Advisory: CVE-2022-41254
Aliases: GHSA-74x9-fhc2-p79f
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-09-21
Source: https://osv.dev/vulnerability/CVE-2022-41254
Type: osv

## Details
Missing permission checks in Jenkins CONS3RT Plugin 1.0.0 and earlier allow attackers with Overall/Read permission to connect to an attacker-specified HTTP server using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

## References
- http://www.openwall.com/lists/oss-security/2022/09/21/5
- https://www.jenkins.io/security/advisory/2022-09-21/#SECURITY-2751
