# [C] Incorrect Authorization in Puppet Enterprise Pipeline Jenkins Plugin

## Summary
Severity: Critical
Advisory: GHSA-mj9c-vjp9-pggh
CVE: CVE-2019-10458
CWE: CWE-183, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-mj9c-vjp9-pggh
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins.workflow:puppet-enterprise-pipeline` — affected >=0

## Details
Jenkins Puppet Enterprise Pipeline 1.3.1 and earlier specifies unsafe values in its custom Script Security whitelist, allowing attackers able to execute Script Security protected scripts to execute arbitrary code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10458
- https://github.com/jenkinsci/puppet-enterprise-pipeline-plugin
- https://jenkins.io/security/advisory/2019-10-16/#SECURITY-918
