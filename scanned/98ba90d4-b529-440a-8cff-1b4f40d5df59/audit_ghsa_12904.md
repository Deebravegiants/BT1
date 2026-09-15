# [C] Agent-to-controller security bypass in Jenkins Semantic Versioning Plugin 

## Summary
Severity: Critical
Advisory: GHSA-pcc2-w6m8-x5w4
CVE: CVE-2023-24429
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-pcc2-w6m8-x5w4
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:semantic-versioning-plugin` — affected >=0 <1.15

## Details
Jenkins Semantic Versioning Plugin 1.14 and earlier does not restrict execution of an controller/agent message to agents, and implements no limitations about the file path that can be parsed, allowing attackers able to control agent processes to have Jenkins parse a crafted file that uses external entities for extraction of secrets from the Jenkins controller or server-side request forgery.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24429
- https://github.com/jenkinsci/semantic-versioning-plugin/commit/c67a89822f86a7d10498ea2783b833052b719086
- https://github.com/jenkinsci/semantic-versioning-plugin
- https://www.jenkins.io/security/advisory/2023-01-24/#SECURITY-2973%20(1)
