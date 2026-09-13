# [H] Remote code execution vulnerability in Jenkins Templating Engine Plugin

## Summary
Severity: High
Advisory: GHSA-p6qc-37hq-wqr6
CVE: CVE-2021-21646
CWE: CWE-693
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-p6qc-37hq-wqr6
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:templating-engine` — affected >=0 <2.2

## Details
Jenkins Templating Engine Plugin 2.1 and earlier does not protect its pipeline configurations using Script Security Plugin.

This vulnerability allows attackers with Job/Configure permission to execute arbitrary code in the context of the Jenkins controller JVM.

Jenkins Templating Engine Plugin 2.2 integrates with Script Security Plugin to protect its pipeline configurations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21646
- https://github.com/jenkinsci/templating-engine-plugin/commit/aed14bed7333329f51330d0a8111e4d94cdee3e6
- https://github.com/jenkinsci/templating-engine-plugin
- https://www.jenkins.io/security/advisory/2021-04-21/#SECURITY-2311
- http://www.openwall.com/lists/oss-security/2021/04/21/2
