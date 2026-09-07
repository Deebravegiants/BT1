# [H] Jenkins Dynatrace Plugin vulnerable to Cross-Site Request Forgery

## Summary
Severity: High
Advisory: GHSA-x546-xrx3-hjx4
CVE: CVE-2019-10462
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-x546-xrx3-hjx4
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:dynatrace-dashboard` — affected >=0 <2.1.4

## Details
A cross-site request forgery vulnerability in Jenkins Dynatrace Application Monitoring Plugin prior to 2.1.4 allows attackers to connect to an attacker-specified URL using attacker-specified credentials.

##NOTE: This plugin is marked as DEPRECATED

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10462
- https://github.com/jenkinsci/dynatrace-plugin/commit/373adaa1161d59ccd4e5e3469a9b6aeec17968ae
- https://github.com/jenkinsci/dynatrace-plugin
- https://jenkins.io/security/advisory/2019-10-23/#SECURITY-1483%20(1)
- http://www.openwall.com/lists/oss-security/2019/10/23/2
