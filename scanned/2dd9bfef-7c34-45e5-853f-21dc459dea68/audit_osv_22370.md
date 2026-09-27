# [M] CVE-2022-27211

## Summary
Severity: Medium
Advisory: CVE-2022-27211
Aliases: GHSA-794j-hx96-4w3m
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-03-15
Source: https://osv.dev/vulnerability/CVE-2022-27211
Type: osv

## Details
A missing permission check in Jenkins Kubernetes Continuous Deploy Plugin 2.3.1 and earlier allows attackers with Overall/Read permission to connect to an attacker-specified SSH server using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

## References
- http://www.openwall.com/lists/oss-security/2022/03/15/2
- https://www.jenkins.io/security/advisory/2022-03-15/#SECURITY-2681
