# [M] CVE-2022-36904

## Summary
Severity: Medium
Advisory: CVE-2022-36904
Aliases: GHSA-fjpq-f574-jc45
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-07-27
Source: https://osv.dev/vulnerability/CVE-2022-36904
Type: osv

## Details
Jenkins Repository Connector Plugin 2.2.0 and earlier does not perform a permission check in a method implementing form validation, allowing attackers with Overall/Read permission to check for the existence of an attacker-specified file path on the Jenkins controller file system.

## References
- http://www.openwall.com/lists/oss-security/2022/07/27/1
- https://www.jenkins.io/security/advisory/2022-07-27/#SECURITY-2665%20%282%29
