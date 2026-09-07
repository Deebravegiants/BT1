# [M] Stored XSS vulnerability in Jenkins Repository Connector Plugin

## Summary
Severity: Medium
Advisory: GHSA-hg2w-3c4j-jjwm
CVE: CVE-2021-21618
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-hg2w-3c4j-jjwm
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:repository-connector` — affected >=0 <2.0.3

## Details
Jenkins Repository Connector Plugin 2.0.2 and earlier does not escape parameter names and descriptions for past builds.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Item/Configure permission.

Jenkins Repository Connector Plugin 2.0.3 escapes parameter names and descriptions when creating new parameters.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21618
- https://github.com/jenkinsci/repository-connector-plugin
- https://www.jenkins.io/security/advisory/2021-02-24/#SECURITY-2183
