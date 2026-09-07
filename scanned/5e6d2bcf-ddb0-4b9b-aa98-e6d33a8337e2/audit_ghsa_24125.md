# [H] Cross-Site Request Forgery in Jenkins Git Plugin

## Summary
Severity: High
Advisory: GHSA-rf5q-8gx3-xqfc
CVE: CVE-2017-1000092
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-rf5q-8gx3-xqfc
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:git` — affected >=0 <3.3.2

## Details
Git Plugin connects to a user-specified Git repository as part of form validation. An attacker with no direct access to Jenkins but able to guess at a username/password credentials ID could trick a developer with job configuration permissions into following a link with a maliciously crafted Jenkins URL which would result in the Jenkins Git client sending the username and password to an attacker-controlled server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000092
- https://bugzilla.redhat.com/show_bug.cgi?id=1471053
- https://jenkins.io/security/advisory/2017-07-10
