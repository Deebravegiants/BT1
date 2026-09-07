# [H] Jenkins SAML Plugin does not implement a replay cache

## Summary
Severity: High
Advisory: GHSA-j7r7-7qmf-xq87
CVE: CVE-2025-64131
CWE: CWE-294
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-10-29
Source: https://github.com/advisories/GHSA-j7r7-7qmf-xq87
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:saml` — affected >=0 <4.583.585.v22ccc1139f55

## Details
Jenkins SAML Plugin 4.583.vc68232f7018a_ and earlier does not implement a replay cache.

This allows attackers able to obtain information about the SAML authentication flow between a user’s web browser and Jenkins to replay those requests, authenticating to Jenkins as that user.

SAML Plugin 4.583.585.v22ccc1139f55 implements a replay cache that rejects replayed requests.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-64131
- https://github.com/jenkinsci/saml-plugin/commit/6170b1013daf52770de29a66aeb57893aae1d7d6
- https://github.com/jenkinsci/saml-plugin
- https://www.jenkins.io/security/advisory/2025-10-29/#SECURITY-3613
- http://www.openwall.com/lists/oss-security/2025/10/29/2
