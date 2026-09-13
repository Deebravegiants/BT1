# [M] Jenkins SAML Single Sign On(SSO) Plugin missing permission check

## Summary
Severity: Medium
Advisory: GHSA-p4wr-9wfm-f9jw
CVE: CVE-2023-37945
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-07-12
Source: https://github.com/advisories/GHSA-p4wr-9wfm-f9jw
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:miniorange-saml-sp` — affected >=0 <2.3.1

## Details
Jenkins SAML Single Sign On(SSO) Plugin 2.3.0 and earlier does not perform a permission check in an HTTP endpoint.

This allows attackers with Overall/Read permission to download a string representation of the current security realm (Java `Object#toString()`), which potentially includes sensitive information.

SAML Single Sign On(SSO) Plugin 2.3.1 requires Overall/Administer permission to access the affected HTTP endpoint, and only allows downloading a string representation if the current security realm is this plugin’s.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-37945
- https://www.jenkins.io/security/advisory/2023-07-12/#SECURITY-3164
- http://www.openwall.com/lists/oss-security/2023/07/12/2
