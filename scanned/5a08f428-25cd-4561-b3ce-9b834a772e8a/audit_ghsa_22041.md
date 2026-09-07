# [M] Jenkins GitHub Authentication Plugin Cross-Site Request Forgery vulnerability

## Summary
Severity: Medium
Advisory: GHSA-phwv-crgp-9r69
CVE: CVE-2019-10315
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-phwv-crgp-9r69
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:github-oauth` — affected >=0 <0.32

## Details
Jenkins GitHub Authentication Plugin did not manage the state parameter of OAuth to prevent CSRF. This allowed an attacker to catch the redirect URL provided during the authentication process using OAuth and send it to the victim. If the victim was already connected to Jenkins, their Jenkins account would be attached to the attacker’s GitHub account.

The state parameter is now correctly managed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10315
- https://jenkins.io/security/advisory/2019-04-30/#SECURITY-443
- https://web.archive.org/web/20200227073756/http://www.securityfocus.com/bid/108159
- http://www.openwall.com/lists/oss-security/2019/04/30/5
