# [M] Missing permission checks in Jenkins Proxmox Plugin 

## Summary
Severity: Medium
Advisory: GHSA-2mgj-mwvf-mpg5
CVE: CVE-2022-28144
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-03-30
Source: https://github.com/advisories/GHSA-2mgj-mwvf-mpg5
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:proxmox` — affected >=0 <0.7.1

## Details
Jenkins Proxmox Plugin 0.7.0 and earlier does not perform a permission check in several HTTP endpoints, allowing attackers with Overall/Read permission to connect to an attacker-specified host using attacker-specified username and password (perform a connection test), disable SSL/TLS validation for the entire Jenkins controller JVM as part of the connection test (see CVE-2022-28142), and test a rollback with attacker-specified parameters.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-28144
- https://www.jenkins.io/security/advisory/2022-03-29/#SECURITY-2082
- http://www.openwall.com/lists/oss-security/2022/03/29/1
