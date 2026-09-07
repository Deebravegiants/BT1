# [H] Jenkins Assembla Auth Plugin vulnerable to cross-site request forgery

## Summary
Severity: High
Advisory: GHSA-p756-66w2-35g7
CVE: CVE-2023-37961
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-12
Source: https://github.com/advisories/GHSA-p756-66w2-35g7
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:assembla-auth` — affected >=0

## Details
Jenkins Assembla Auth Plugin 1.14 and earlier does not implement a state parameter in its OAuth flow, a unique and non-guessable value associated with each authentication request.

This vulnerability allows attackers to trick users into logging in to the attacker’s account.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-37961
- https://www.jenkins.io/security/advisory/2023-07-12/#SECURITY-2988
- http://www.openwall.com/lists/oss-security/2023/07/12/2
