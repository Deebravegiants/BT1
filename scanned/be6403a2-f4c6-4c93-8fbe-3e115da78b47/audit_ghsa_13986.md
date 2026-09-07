# [H] Jenkins CAS Plugin Session Fixation vulnerability

## Summary
Severity: High
Advisory: GHSA-hjh8-9gxh-cx4x
CVE: CVE-2023-32997
CWE: CWE-384
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-05-16
Source: https://github.com/advisories/GHSA-hjh8-9gxh-cx4x
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:cas-plugin` — affected >=0 <1.6.3

## Details
Jenkins CAS Plugin 1.6.2 and earlier does not invalidate the existing session on login.

This allows attackers to use social engineering techniques to gain administrator access to Jenkins.

CAS Plugin 1.6.3 invalidates the existing session on login.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-32997
- https://github.com/jenkinsci/cas-plugin/commit/3a33cc0175bcc18801faf9125afb38d495b5995f
- https://www.jenkins.io/security/advisory/2023-05-16/#SECURITY-3000
