# [H] Jenkins Accurev Plugin CSRF vulnerability and missing permission checks

## Summary
Severity: High
Advisory: GHSA-8vg7-gh73-866v
CVE: CVE-2018-1999028
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-8vg7-gh73-866v
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:accurev` — affected >=0 <0.7.17

## Details
An exposure of sensitive information vulnerability exists in Jenkins Accurev Plugin 0.7.16 and earlier in AccurevSCM.java that allows attackers to capture credentials with a known credentials ID stored in Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1999028
- https://github.com/jenkinsci/accurev-plugin/commit/a86e05f7747b8f7d483f61a840cfb7a1a0105eee
- https://github.com/jenkinsci/accurev-plugin
- https://jenkins.io/security/advisory/2018-07-30/#SECURITY-1021
