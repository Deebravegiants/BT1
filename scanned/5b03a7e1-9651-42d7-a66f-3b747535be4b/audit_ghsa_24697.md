# [H] Jenkins 360 FireLine Plugin vulnerable to XML External Entity Reference

## Summary
Severity: High
Advisory: GHSA-346g-jrx9-jgf4
CVE: CVE-2019-10466
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-346g-jrx9-jgf4
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins.plugin:fireline` — affected >=0

## Details
An XML external entities (XXE) vulnerability in Jenkins 360 FireLine Plugin allows attackers with Overall/Read access to have Jenkins resolve external entities, resulting in the extraction of secrets from the Jenkins agent, server-side request forgery, or denial-of-service attacks.

## Note: Jenkins has suspended distribution of this plugin.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10466
- https://github.com/jenkinsci/fireline-plugin
- https://jenkins.io/security/advisory/2019-10-23/#SECURITY-822
- http://www.openwall.com/lists/oss-security/2019/10/23/2
