# [H] Cross-site request forgery vulnerability in Jenkins OpenID Plugin

## Summary
Severity: High
Advisory: GHSA-96jv-c7m6-q43g
CVE: CVE-2023-24446
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-96jv-c7m6-q43g
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:openid` — affected >=0

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins OpenID Plugin 2.4 and earlier allows attackers to trick users into logging in to the attacker's account.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24446
- https://www.jenkins.io/security/advisory/2023-01-24/#SECURITY-2995
