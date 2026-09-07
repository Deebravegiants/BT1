# [M] Missing SSH host key validation in Jenkins Amazon EC2 Plugin

## Summary
Severity: Medium
Advisory: GHSA-q8qq-2p5p-rg44
CVE: CVE-2020-2185
CWE: CWE-300
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-q8qq-2p5p-rg44
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:ec2` — affected >=0 <1.50.2

## Details
Jenkins Amazon EC2 Plugin 1.50.1 and earlier does not use SSH host key validation when connecting to agents. This lack of validation could be abused using a man-in-the-middle attack to intercept these connections to build agents.

Jenkins Amazon EC2 Plugin 1.50.2 provides strategies for performing host key validation for administrators to select the one that meets their security needs. It includes assistance for administrators to migrate to a new, more secure strategy. For more information see [the plugin documentation](https://github.com/jenkinsci/ec2-plugin/#securing-the-connection-to-unix-amis).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2185
- https://github.com/jenkinsci/ec2-plugin/commit/4c9f03ae202e4730fd54eda40771fa4d3873e358
- https://github.com/jenkinsci/ec2-plugin
- https://jenkins.io/security/advisory/2020-05-06/#SECURITY-381
- http://www.openwall.com/lists/oss-security/2020/05/06/3
