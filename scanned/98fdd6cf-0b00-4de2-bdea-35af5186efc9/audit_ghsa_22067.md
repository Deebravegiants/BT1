# [M] Improper Limitation of a Pathname to a Restricted Directory in Jenkins Google OAuth Credentials Plugin

## Summary
Severity: Medium
Advisory: GHSA-8qh4-fghr-6fxg
CVE: CVE-2019-10436
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-8qh4-fghr-6fxg
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:google-oauth-plugin` — affected >=0 <0.10

## Details
An arbitrary file read vulnerability in Jenkins Google OAuth Credentials Plugin 0.9 and earlier allowed attackers able to configure jobs and credentials in Jenkins to obtain the contents of any file on the Jenkins master.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10436
- https://github.com/jenkinsci/google-oauth-plugin/commit/aef26a8425e515a9986412000d6191db95fa9e56
- https://github.com/jenkinsci/google-oauth-plugin
- https://jenkins.io/security/advisory/2019-10-16/#SECURITY-1583
