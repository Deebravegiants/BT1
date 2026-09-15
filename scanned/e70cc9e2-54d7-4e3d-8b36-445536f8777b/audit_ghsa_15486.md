# [C] omniauth-saml vulnerable to Improper Verification of Cryptographic Signature

## Summary
Severity: Critical
Advisory: GHSA-cvp8-5r8g-fhvq
CWE: CWE-347
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2024-09-11
Source: https://github.com/advisories/GHSA-cvp8-5r8g-fhvq
Type: github-advisory

## Affected
- RubyGems: `omniauth-saml` — affected >=2.0.0 <2.1.2
- RubyGems: `omniauth-saml` — affected >=0 <1.10.5
- RubyGems: `omniauth-saml` — affected >=2.2.0 <2.2.1

## Details
ruby-saml, the dependent SAML gem of omniauth-saml has a signature wrapping vulnerability in <= v1.12.0 and v1.13.0 to v1.16.0 , see https://github.com/SAML-Toolkits/ruby-saml/security/advisories/GHSA-jw9c-mfg7-9rx2 
As a result, omniauth-saml created a [new release](https://github.com/omniauth/omniauth-saml/releases) by upgrading ruby-saml to the patched versions v1.17.

## References
- https://github.com/SAML-Toolkits/ruby-saml/security/advisories/GHSA-jw9c-mfg7-9rx2
- https://github.com/omniauth/omniauth-saml/security/advisories/GHSA-cvp8-5r8g-fhvq
- https://github.com/omniauth/omniauth-saml/commit/4274e9d57e65f2dcaae4aa3b2accf831494f2ddd
- https://github.com/omniauth/omniauth-saml/commit/6c681fd082ab3daf271821897a40ab3417382e29
- https://github.com/omniauth/omniauth-saml
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/omniauth-saml/GHSA-cvp8-5r8g-fhvq.yml
