# [H] Jenkins Azure AD Plugin allows bypassing CSRF protection for any URL

## Summary
Severity: High
Advisory: GHSA-x77r-7m5w-pqq2
CVE: CVE-2021-21679
CWE: CWE-352, CWE-693
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-x77r-7m5w-pqq2
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:azure-ad` — affected >=0 <180.v8b1e80e6f242

## Details
An extension point in Jenkins allows selectively disabling cross-site request forgery (CSRF) protection for specific URLs. Jenkins Azure AD Plugin implements this extension point for URLs used by a JavaScript component.

In Jenkins Azure AD Plugin 179.vf6841393099e and earlier this implementation is too permissive, allowing attackers to craft URLs that would bypass the CSRF protection of any target URL.

This vulnerability was originally introduced in Azure AD Plugin 164.v5b48baa961d2.

Azure AD Plugin 180.v8b1e80e6f242 no longer allows bypassing CSRF protection for URLs used by the JavaScript component. Instead, that component was reconfigured to pass the expected CSRF token.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21679
- https://github.com/jenkinsci/azure-ad-plugin/commit/8b1e80e6f242275127ebb177e2a755a2104b4853
- https://github.com/jenkinsci/azure-ad-plugin
- https://www.jenkins.io/security/advisory/2021-08-31/#SECURITY-2470
- http://www.openwall.com/lists/oss-security/2021/08/31/1
