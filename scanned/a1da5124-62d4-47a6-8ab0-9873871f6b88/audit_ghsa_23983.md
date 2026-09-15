# [M] Jenkins GitHub Pull Request Builder Plugin allows attacker with local file system access to obtain GitHub credentials

## Summary
Severity: Medium
Advisory: GHSA-hr74-2j5v-ghfv
CVE: CVE-2018-1000142
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-hr74-2j5v-ghfv
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:ghprb` — affected >=0 <1.40.0

## Details
An exposure of sensitive information vulnerability exists in Jenkins GitHub Pull Request Builder Plugin version 1.39.0 and older in GhprbCause.java that allows an attacker with local file system access to obtain GitHub credentials. Since 1.40.0, the plugin no longer stores serialized objects containing the credential on disk. Builds started before the plugin was updated to 1.40.0 will retain the encoded credentials on disk. We strongly recommend revoking old GitHub credentials used in Jenkins. We’re providing a script for use in the Script Console that will attempt to remove old stored credentials from build.xml files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000142
- https://github.com/jenkinsci/ghprb-plugin
- https://jenkins.io/security/advisory/2018-03-26/#SECURITY-261
