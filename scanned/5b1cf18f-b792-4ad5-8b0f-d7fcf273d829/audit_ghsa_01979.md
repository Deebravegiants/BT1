# [H] CSRF vulnerability in Jenkins Xray - Test Management for Jira Plugin allows capturing credentials

## Summary
Severity: High
Advisory: GHSA-rrvg-2c69-p9rf
CVE: CVE-2021-21652
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2021-06-16
Source: https://github.com/advisories/GHSA-rrvg-2c69-p9rf
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:xray-connector` — affected >=0 <2.4.1

## Details
Jenkins Xray - Test Management for Jira Plugin 2.4.0 and earlier does not require POST requests for a connection test method, resulting in a cross-site request forgery (CSRF) vulnerability.

This vulnerability allows attackers to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

Jenkins Xray - Test Management for Jira Plugin 2.4.1 requires POST requests for the affected connection test method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21652
- https://github.com/jenkinsci/xray-connector-plugin
- https://www.jenkins.io/security/advisory/2021-05-11/#SECURITY-2251%20(1)
