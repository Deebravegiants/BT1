# [M] CSRF vulnerability in Jenkins Gearman Plugin

## Summary
Severity: Medium
Advisory: GHSA-449p-7c3p-vf7g
CVE: CVE-2019-1003082
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-449p-7c3p-vf7g
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:gearman-plugin` — affected >=0 <0.4.0

## Details
A cross-site request forgery vulnerability in Jenkins Gearman Plugin in the GearmanPluginConfig#doTestConnection form validation method allows attackers to initiate a connection to an attacker-specified server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003082
- https://jenkins.io/security/advisory/2019-04-03/#SECURITY-991
- http://www.openwall.com/lists/oss-security/2019/04/12/2
- http://www.securityfocus.com/bid/107790
