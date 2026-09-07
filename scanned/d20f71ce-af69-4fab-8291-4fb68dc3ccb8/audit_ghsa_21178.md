# [M] Jenkins Matrix Reloaded Plugin vulnerable to CSRF

## Summary
Severity: Medium
Advisory: GHSA-4v5c-5v6c-37pj
CVE: CVE-2022-34789
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-07-01
Source: https://github.com/advisories/GHSA-4v5c-5v6c-37pj
Type: github-advisory

## Affected
- Maven: `net.praqma:matrix-reloaded` — affected >=0

## Details
Jenkins Matrix Reloaded Plugin 1.1.3 and earlier does not require POST requests for an HTTP endpoint, resulting in a cross-site request forgery (CSRF) vulnerability. This vulnerability allows attackers to rebuild previous matrix builds.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34789
- https://github.com/jenkinsci/matrix-reloaded-plugin
- https://www.jenkins.io/security/advisory/2022-06-30/#SECURITY-2016
