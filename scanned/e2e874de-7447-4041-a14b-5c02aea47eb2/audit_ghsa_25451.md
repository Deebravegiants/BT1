# [H] XXE vulnerability in Jenkins Robot Framework Plugin

## Summary
Severity: High
Advisory: GHSA-m53p-f25q-q6fg
CVE: CVE-2020-2092
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-m53p-f25q-q6fg
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:robot` — affected >=0 <2.0.1

## Details
Robot Framework Plugin 2.0.0 and earlier does not configure the XML parser to prevent XML external entity (XXE) attacks.

This allows a user able to control the input files for the 'Publish Robot Framework' post-build step to have Jenkins parse a crafted file that uses external entities for extraction of secrets from the Jenkins controller, server-side request forgery, or denial-of-service attacks.

Robot Framework Plugin 2.0.1 disables external entity resolution for its XML parser.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2092
- https://github.com/jenkinsci/robot-plugin/commit/a06626f516e63813db570ff9f3e9b1f76012df59
- https://github.com/jenkinsci/robot-plugin
- https://jenkins.io/security/advisory/2020-01-15/#SECURITY-1698
