# [M] Incorrect Authorization in Jenkins Gerrit Trigger Plugin

## Summary
Severity: Medium
Advisory: GHSA-4vf2-cm23-rf4c
CVE: CVE-2018-1000106
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-4vf2-cm23-rf4c
Type: github-advisory

## Affected
- Maven: `com.sonyericsson.hudson.plugins.gerrit:gerrit-trigger` — affected >=0 <2.27.5

## Details
An improper authorization vulnerability exists in Jenkins Gerrit Trigger Plugin 2.27.4 and earlier in GerritManagement.java, GerritServer.java, and PluginImpl.java that allows an attacker with Overall/Read access to modify the Gerrit configuration in Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000106
- https://github.com/jenkinsci/gerrit-trigger-plugin/commit/a222f2d9d1bca3422e6a462a7f587ae325455b80
- https://jenkins.io/security/advisory/2018-02-26/#SECURITY-403
