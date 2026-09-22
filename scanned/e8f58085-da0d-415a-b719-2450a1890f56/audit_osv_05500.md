# [C] ruby-saml vulnerable to SAML authentication bypass due to DOCTYPE handling (parser differential)

## Summary
Severity: Critical
Advisory: BIT-gitlab-2025-25291
Aliases: CVE-2025-25291, GHSA-4vc4-m8qh-g8jm
Ecosystem: Bitnami
Published: 2025-04-14
Source: https://osv.dev/vulnerability/BIT-gitlab-2025-25291
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=0 <17.9.2

## Details
ruby-saml provides security assertion markup language (SAML) single sign-on (SSO) for Ruby. An authentication bypass vulnerability was found in ruby-saml prior to versions 1.12.4 and 1.18.0 due to a parser differential. ReXML and Nokogiri parse XML differently; the parsers can generate entirely different document structures from the same XML input. That allows an attacker to be able to execute a Signature Wrapping attack. This issue may lead to authentication bypass. Versions 1.12.4 and 1.18.0 fix the issue.

## References
- https://about.gitlab.com/releases/2025/03/12/patch-release-gitlab-17-9-2-released
- https://github.blog/security/sign-in-as-anyone-bypassing-saml-sso-authentication-with-parser-differentials
- https://github.com/SAML-Toolkits/ruby-saml/commit/e76c5b36bac40aedbf1ba7ffaaf495be63328cd9
- https://github.com/SAML-Toolkits/ruby-saml/commit/e9c1cdbd0f9afa467b585de279db0cbd0fb8ae97
- https://github.com/SAML-Toolkits/ruby-saml/releases/tag/v1.12.4
- https://github.com/SAML-Toolkits/ruby-saml/releases/tag/v1.18.0
- https://github.com/SAML-Toolkits/ruby-saml/security/advisories/GHSA-4vc4-m8qh-g8jm
- https://github.com/omniauth/omniauth-saml/security/advisories/GHSA-hw46-3hmr-x9xv
- https://news.ycombinator.com/item?id=43374519
- https://nvd.nist.gov/vuln/detail/CVE-2025-25291
- https://portswigger.net/research/saml-roulette-the-hacker-always-wins
- https://security.netapp.com/advisory/ntap-20250314-0010/
- https://securitylab.github.com/advisories/GHSL-2024-329_GHSL-2024-330_ruby-saml
- https://lists.debian.org/debian-lts-announce/2025/04/msg00011.html
