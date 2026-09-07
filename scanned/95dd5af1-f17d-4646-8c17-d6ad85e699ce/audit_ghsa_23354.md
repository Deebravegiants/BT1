# [M] Jenkins OpenID Plugin CSRF vulnerability

## Summary
Severity: Medium
Advisory: GHSA-8v26-3p83-mf2g
CVE: CVE-2019-1003098
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-8v26-3p83-mf2g
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:openid` — affected >=0 <2.4

## Details
A cross-site request forgery vulnerability in Jenkins openid Plugin in the OpenIdSsoSecurityRealm.DescriptorImpl#doValidate form validation method allows attackers to initiate a connection to an attacker-specified server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003098
- https://github.com/jenkinsci/openid-plugin/commit/5a91a74a94e44d87cd61afc2441aab42b7542bf0
- https://github.com/jenkinsci/openid-plugin
- https://jenkins.io/security/advisory/2019-04-03/#SECURITY-1084
- http://www.openwall.com/lists/oss-security/2019/04/12/2
- http://www.securityfocus.com/bid/107790
