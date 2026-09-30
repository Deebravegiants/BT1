# [H] XML External Entity Reference vulnerability in Jenkins Config File Provider Plugin

## Summary
Severity: High
Advisory: GHSA-q7xg-hh3q-hc68
CVE: CVE-2021-21642
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-q7xg-hh3q-hc68
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:config-file-provider` — affected >=0 <3.7.1

## Details
Jenkins Config File Provider Plugin 3.7.0 and earlier does not configure its XML parser to prevent XML external entity (XXE) attacks.

This allows attackers with the ability to define Maven configuration files to have Jenkins parse a crafted configuration file that uses external entities for extraction of secrets from the Jenkins controller or server-side request forgery.

Jenkins Config File Provider Plugin 3.7.1 disables external entity resolution for its XML parser.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21642
- https://github.com/jenkinsci/config-file-provider-plugin/commit/5f845bc015be769e595088bab11ec36c767671e1
- https://github.com/jenkinsci/config-file-provider-plugin
- https://www.jenkins.io/security/advisory/2021-04-21/#SECURITY-2204
- http://www.openwall.com/lists/oss-security/2021/04/21/2
