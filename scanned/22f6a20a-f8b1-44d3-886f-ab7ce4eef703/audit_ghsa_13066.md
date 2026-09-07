# [M] Jenkins Favorite View Plugin cross-site request forgery vulnerability

## Summary
Severity: Medium
Advisory: GHSA-jrj6-qx48-3cpq
CVE: CVE-2023-40351
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-08-16
Source: https://github.com/advisories/GHSA-jrj6-qx48-3cpq
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:favorite-view` — affected >=0

## Details
Jenkins Favorite View Plugin 5.v77a_37f62782d and earlier does not require POST requests for an HTTP endpoint, resulting in a cross-site request forgery (CSRF) vulnerability.

This vulnerability allows attackers to add or remove views from another user’s favorite views tab bar.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-40351
- https://www.jenkins.io/security/advisory/2023-08-16/#SECURITY-3201
- http://www.openwall.com/lists/oss-security/2023/08/16/3
