# [M] Missing permission check in Jenkins jenkins-reviewbot Plugin

## Summary
Severity: Medium
Advisory: GHSA-2r46-cwgm-vvjx
CVE: CVE-2019-10279
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-2r46-cwgm-vvjx
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:jenkins-reviewbot` — affected >=0

## Details
A missing permission check in Jenkins jenkins-reviewbot Plugin in the ReviewboardDescriptor#doTestConnection form validation method allows attackers with Overall/Read permission to initiate a connection to an attacker-specified server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10279
- https://jenkins.io/security/advisory/2019-04-03/#SECURITY-1091
- http://www.openwall.com/lists/oss-security/2019/04/12/2
- http://www.securityfocus.com/bid/107790
