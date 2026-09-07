# [M] Cross-site request forgery vulnerability in Jenkins Nomad Plugin

## Summary
Severity: Medium
Advisory: GHSA-5q63-jvc9-qphv
CVE: CVE-2019-1003092
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-5q63-jvc9-qphv
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:nomad` — affected >=0 <0.5.1

## Details
A cross-site request forgery vulnerability in Jenkins Nomad Plugin in the NomadCloud.DescriptorImpl#doTestConnection form validation method allows attackers to initiate a connection to an attacker-specified server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003092
- https://github.com/jenkinsci/nomad-plugin/commit/3331d24896b815c375e528207c5572e18631c49d
- https://github.com/jenkinsci/nomad-plugin
- https://jenkins.io/security/advisory/2019-04-03/#SECURITY-1058
- http://www.openwall.com/lists/oss-security/2019/04/12/2
- http://www.securityfocus.com/bid/107790
