# [H] Ruby SAML allows remote Denial of Service (DoS) with compressed SAML responses

## Summary
Severity: High
Advisory: GHSA-92rq-c8cf-prrq
CVE: CVE-2025-25293
CWE: CWE-400, CWE-770
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-12
Source: https://github.com/advisories/GHSA-92rq-c8cf-prrq
Type: github-advisory

## Affected
- RubyGems: `ruby-saml` — affected >=0 <1.12.4
- RubyGems: `ruby-saml` — affected >=1.13.0 <1.18.0

## Details
### Summary
ruby-saml is susceptible to remote Denial of Service (DoS) with compressed SAML responses.

Ruby-saml uses zlib to decompress SAML responses in case they're compressed. It is possible to bypass the message size check with a compressed assertion since the message size is checked before inflation and not after.

### Impact
This issue may lead to remote Denial of Service (DoS).

## References
- https://github.com/SAML-Toolkits/ruby-saml/security/advisories/GHSA-92rq-c8cf-prrq
- https://github.com/omniauth/omniauth-saml/security/advisories/GHSA-hw46-3hmr-x9xv
- https://nvd.nist.gov/vuln/detail/CVE-2025-25293
- https://github.com/SAML-Toolkits/ruby-saml/commit/acac9e9cc0b9a507882c614f25d41f8b47be349a
- https://github.com/SAML-Toolkits/ruby-saml/commit/e2da4c6dae7dc01a4d9cd221395140a67e2b3eb1
- https://about.gitlab.com/releases/2025/03/12/patch-release-gitlab-17-9-2-released
- https://github.blog/security/sign-in-as-anyone-bypassing-saml-sso-authentication-with-parser-differentials
- https://github.com/SAML-Toolkits/ruby-saml
- https://github.com/SAML-Toolkits/ruby-saml/releases/tag/v1.12.4
- https://github.com/SAML-Toolkits/ruby-saml/releases/tag/v1.18.0
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/ruby-saml/CVE-2025-25293.yml
- https://lists.debian.org/debian-lts-announce/2025/04/msg00011.html
- https://security.netapp.com/advisory/ntap-20250314-0008
- https://securitylab.github.com/advisories/GHSL-2024-355_ruby-saml
