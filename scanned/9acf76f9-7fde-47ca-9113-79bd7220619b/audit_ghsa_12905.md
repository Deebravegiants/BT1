# [M] Cross-site request forgery vulnerability in Jenkins Bitbucket OAuth Plugin 

## Summary
Severity: Medium
Advisory: GHSA-685j-36qx-3vp2
CVE: CVE-2023-24428
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-685j-36qx-3vp2
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:bitbucket-oauth` — affected >=0 <0.13

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins Bitbucket OAuth Plugin 0.12 and earlier allows attackers to trick users into logging in to the attacker's account.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24428
- https://github.com/jenkinsci/bitbucket-oauth-plugin/commit/a927a8ff2e069afebb97f33f6798033ef4451e4f
- https://github.com/jenkinsci/bitbucket-oauth-plugin
- https://www.jenkins.io/security/advisory/2023-01-24/#SECURITY-2981
