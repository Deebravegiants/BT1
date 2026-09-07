# [M] CSRF vulnerability in Jenkins P4 Plugin

## Summary
Severity: Medium
Advisory: GHSA-rjjq-63c7-8724
CVE: CVE-2020-2141
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-rjjq-63c7-8724
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:p4` — affected >=0 <1.10.11

## Details
A cross-site request forgery vulnerability in Jenkins P4 Plugin 1.10.10 and earlier allows attackers to trigger builds or add a labels in Perforce.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2141
- https://github.com/jenkinsci/p4-plugin/commit/2f2a31d8d36de7abab45820fab3a82f4c682b760
- https://github.com/jenkinsci/p4-plugin
- https://jenkins.io/security/advisory/2020-03-09/#SECURITY-1765
- http://www.openwall.com/lists/oss-security/2020/03/09/1
