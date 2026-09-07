# [M] XSS vulnerability in Jenkins Claim Plugin

## Summary
Severity: Medium
Advisory: GHSA-48hr-jg4p-w4p4
CVE: CVE-2021-21619
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-48hr-jg4p-w4p4
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:claim` — affected >=0 <2.18.2

## Details
Jenkins Claim Plugin 2.18.1 and earlier does not escape the user display name shown in claims.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by attackers who are able to control the display names of Jenkins users, either via the security realm, or directly inside Jenkins.

Everyone with a Jenkins account can change their own display name.\n\nClaim Plugin 2.18.2 escapes the user display name shown in claims.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21619
- https://github.com/jenkinsci/claim-plugin
- https://www.jenkins.io/security/advisory/2021-02-24/#SECURITY-2188%20(1)
- http://www.openwall.com/lists/oss-security/2021/02/24/3
