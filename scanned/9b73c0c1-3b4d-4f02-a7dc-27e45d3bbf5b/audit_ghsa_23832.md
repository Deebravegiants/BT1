# [M] Jenkins Nomad Plugin missing permission check

## Summary
Severity: Medium
Advisory: GHSA-p278-2qh9-6mwj
CVE: CVE-2019-1003093
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-p278-2qh9-6mwj
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:nomad` — affected >=0 <0.6.3

## Details
A missing permission check in Jenkins Nomad Plugin in the NomadCloud.DescriptorImpl#doTestConnection form validation method allows attackers with Overall/Read permission to initiate a connection to an attacker-specified server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003093
- https://github.com/jenkinsci/nomad-plugin/commit/93ea215a649575e4063e1dfe8361b684c29a91e3
- https://github.com/jenkinsci/nomad-plugin
- https://github.com/jenkinsci/nomad-plugin/releases/tag/v0.6.3
- https://jenkins.io/security/advisory/2019-04-03/#SECURITY-1058
- http://www.openwall.com/lists/oss-security/2019/04/12/2
- http://www.securityfocus.com/bid/107790
