# [M] GitHub Authentication Plugin session fixation vulnerability

## Summary
Severity: Medium
Advisory: GHSA-mcqx-wc2j-qx9v
CVE: CVE-2019-1003019
CWE: CWE-384
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-mcqx-wc2j-qx9v
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:github-oauth` — affected >=0 <0.31

## Details
An session fixation vulnerability exists in Jenkins GitHub Authentication Plugin 0.29 and earlier in GithubSecurityRealm.java that allows unauthorized attackers to impersonate another user if they can control the pre-authentication session.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003019
- https://github.com/jenkinsci/github-oauth-plugin/commit/3fcc367022c58486e5f52def3edbac92ed258ba4
- https://github.com/jenkinsci/github-oauth-plugin
- https://jenkins.io/security/advisory/2019-01-28/#SECURITY-797
