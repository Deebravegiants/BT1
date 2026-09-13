# [H] CVE-2022-36921

## Summary
Severity: High
Advisory: CVE-2022-36921
Aliases: GHSA-99mq-hw5m-gwjj
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2022-07-27
Source: https://osv.dev/vulnerability/CVE-2022-36921
Type: osv

## Details
A missing permission check in Jenkins Coverity Plugin 1.11.4 and earlier allows attackers with Overall/Read permission to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

## References
- http://www.openwall.com/lists/oss-security/2022/07/27/1
- https://www.jenkins.io/security/advisory/2022-07-27/#SECURITY-2790%20%282%29
