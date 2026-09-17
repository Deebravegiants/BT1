# [M] Exposure of sensitive information in Anchore Container Image Scanner Jenkins Plugin

## Summary
Severity: Medium
Advisory: GHSA-w9v7-7mq5-p27c
CVE: CVE-2018-1999033
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-w9v7-7mq5-p27c
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:anchore-container-scanner` — affected >=0 <1.0.17

## Details
An exposure of sensitive information vulnerability exists in Jenkins Anchore Container Image Scanner Plugin 10.16 and earlier in AnchoreBuilder.java that allows attackers with Item/ExtendedRead permission or file system access to the Jenkins master to obtain the password stored in this plugin's configuration.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1999033
- https://github.com/jenkinsci/anchore-container-scanner-plugin
- https://jenkins.io/security/advisory/2018-07-30/#SECURITY-1039
