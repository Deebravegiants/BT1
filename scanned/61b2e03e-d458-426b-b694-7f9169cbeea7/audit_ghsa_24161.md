# [M] CSRF vulnerability in jenkins-reviewbot Plugin

## Summary
Severity: Medium
Advisory: GHSA-g3rg-cj5x-3vpf
CVE: CVE-2019-10278
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-g3rg-cj5x-3vpf
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:jenkins-reviewbot` — affected >=0

## Details
A cross-site request forgery vulnerability in Jenkins jenkins-reviewbot Plugin in the ReviewboardDescriptor#doTestConnection form validation method allows attackers to initiate a connection to an attacker-specified server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10278
- https://jenkins.io/security/advisory/2019-04-03/#SECURITY-1091
- http://www.openwall.com/lists/oss-security/2019/04/12/2
- http://www.securityfocus.com/bid/107790
