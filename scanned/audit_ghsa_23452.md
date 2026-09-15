# [M] Jenkins Jira Plugin Incorrect Authorization vulnerability

## Summary
Severity: Medium
Advisory: GHSA-fpg6-xqj4-j7wf
CVE: CVE-2018-1000412
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-fpg6-xqj4-j7wf
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:jira` — affected >=0 <3.0.2

## Details
An improper authorization vulnerability exists in Jenkins Jira Plugin 3.0.1 and earlier in JiraSite.java that allows attackers with Overall/Read access to have Jenkins connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins. In version 3.0.2, this form validation method requires POST requests and Overall/Administer (for globally defined sites) or Item/Configure permissions (for sites defined for a folder).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000412
- https://github.com/jenkinsci/jira-plugin/commit/612a6ef06dbd5a63bea0b128142c726e96195eda
- https://jenkins.io/security/advisory/2018-09-25/#SECURITY-1029
- http://www.securityfocus.com/bid/106532
