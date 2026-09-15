# [C] Ruby SAML allows a SAML authentication bypass due to namespace handling (parser differential)

## Summary
Severity: Critical
Advisory: GHSA-754f-8gm6-c4r2
CVE: CVE-2025-25292
CWE: CWE-347, CWE-436
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-03-12
Source: https://github.com/advisories/GHSA-754f-8gm6-c4r2
Type: github-advisory

## Affected
- RubyGems: `ruby-saml` — affected >=1.13.0 <1.18.0
- RubyGems: `ruby-saml` — affected >=0 <1.12.4

## Details
### Summary
An authentication bypass vulnerability was found in ruby-saml due to a parser differential.
ReXML and Nokogiri parse XML differently, the parsers can generate entirely different document structures from the same XML input. That allows an attacker to be able to execute a Signature Wrapping attack.

### Impact
This issue may lead to authentication bypass.

## References
- https://github.com/SAML-Toolkits/ruby-saml/security/advisories/GHSA-754f-8gm6-c4r2
- https://github.com/omniauth/omniauth-saml/security/advisories/GHSA-hw46-3hmr-x9xv
- https://nvd.nist.gov/vuln/detail/CVE-2025-25292
- https://github.com/SAML-Toolkits/ruby-saml/commit/e76c5b36bac40aedbf1ba7ffaaf495be63328cd9
- https://github.com/SAML-Toolkits/ruby-saml/commit/e9c1cdbd0f9afa467b585de279db0cbd0fb8ae97
- https://about.gitlab.com/releases/2025/03/12/patch-release-gitlab-17-9-2-released
- https://github.blog/security/sign-in-as-anyone-bypassing-saml-sso-authentication-with-parser-differentials
- https://github.com/SAML-Toolkits/ruby-saml
- https://github.com/SAML-Toolkits/ruby-saml/releases/tag/v1.12.4
- https://github.com/SAML-Toolkits/ruby-saml/releases/tag/v1.18.0
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/ruby-saml/CVE-2025-25292.yml
- https://lists.debian.org/debian-lts-announce/2025/04/msg00011.html
- https://news.ycombinator.com/item?id=43374519
- https://portswigger.net/research/saml-roulette-the-hacker-always-wins
- https://security.netapp.com/advisory/ntap-20250314-0009
- https://securitylab.github.com/advisories/GHSL-2024-329_GHSL-2024-330_ruby-saml
