# [M] CVE-2019-10465

## Summary
Severity: Medium
Advisory: CVE-2019-10465
Aliases: GHSA-89vj-rqv8-7737
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-10-23
Source: https://osv.dev/vulnerability/CVE-2019-10465
Type: osv

## Details
A missing permission check in Jenkins Deploy WebLogic Plugin allows attackers with Overall/Read permission to connect to an attacker-specified URL using attacker-specified credentials, or determine whether a file or directory with an attacker-specified path exists on the Jenkins master file system.

## References
- http://www.openwall.com/lists/oss-security/2019/10/23/2
- https://jenkins.io/security/advisory/2019-10-23/#SECURITY-820
