# [H] Jenkins SAML Plugin allows bypassing CSRF protection for any URL

## Summary
Severity: High
Advisory: GHSA-r5w3-pfq8-3r82
CVE: CVE-2021-21678
CWE: CWE-352, CWE-693
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-r5w3-pfq8-3r82
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:saml` — affected >=0 <2.0.8

## Details
An extension point in Jenkins allows selectively disabling cross-site request forgery (CSRF) protection for specific URLs. SAML Plugin implements this extension point for the URL that users are redirected to after login.

In Jenkins SAML Plugin 2.0.7 and earlier this implementation is too permissive, allowing attackers to craft URLs that would bypass the CSRF protection of any target URL.\n\nThis vulnerability was originally introduced in Jenkins SAML Plugin 1.1.3.

Jenkins SAML Plugin 2.0.8 restricts which URLs it disables cross-site request forgery (CSRF) protection for to the one URL that needs it.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21678
- https://github.com/jenkinsci/saml-plugin/commit/e063317ee7e1c64a096e0ac323c7155b786c8b9d
- https://github.com/jenkinsci/saml-plugin
- https://www.jenkins.io/security/advisory/2021-08-31/#SECURITY-2469
- http://www.openwall.com/lists/oss-security/2021/08/31/1
