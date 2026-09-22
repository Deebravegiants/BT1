# [M] Jenkins Bitbucket OAuth Plugin does not restrict the redirect URL after login

## Summary
Severity: Medium
Advisory: GHSA-r8fj-rff6-f7h5
CVE: CVE-2026-48924
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-r8fj-rff6-f7h5
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:bitbucket-oauth` — affected >=0 <0.18

## Details
Jenkins Bitbucket OAuth Plugin 0.17 and earlier does not restrict the redirect URL after login.

This allows attackers to perform phishing attacks by having users go to a Jenkins URL that will forward them to a different site after successful authentication.

Bitbucket OAuth Plugin 0.18 only redirects to relative (Jenkins) URLs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-48924
- https://github.com/jenkinsci/bitbucket-oauth-plugin
- https://www.jenkins.io/security/advisory/2026-05-27/#SECURITY-3761
