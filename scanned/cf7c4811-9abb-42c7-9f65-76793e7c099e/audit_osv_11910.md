# [M] CVE-2018-1000068

## Summary
Severity: Medium
Advisory: CVE-2018-1000068
Aliases: GHSA-x6jw-2f23-mc5j
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2018-02-16
Source: https://osv.dev/vulnerability/CVE-2018-1000068
Type: osv

## Details
An improper input validation vulnerability exists in Jenkins versions 2.106 and earlier, and LTS 2.89.3 and earlier, that allows an attacker to access plugin resource files in the META-INF and WEB-INF directories that should not be accessible, if the Jenkins home directory is on a case-insensitive file system.

## References
- http://www.securityfocus.com/bid/103101
- https://jenkins.io/security/advisory/2018-02-14/#SECURITY-717
- https://www.oracle.com/security-alerts/cpuapr2022.html
