# [H] OmniAuth-SAML authentication bypass via incorrect XML canonicalization and DOM traversal

## Summary
Severity: High
Advisory: GHSA-94hm-8q65-rmxm
CVE: CVE-2017-11430
CWE: CWE-287
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2019-07-05
Source: https://github.com/advisories/GHSA-94hm-8q65-rmxm
Type: github-advisory

## Affected
- RubyGems: `omniauth-saml` — affected >=0 <1.10.0

## Details
OmniAuth OmniAuth-SAML 1.9.0 and earlier may incorrectly utilize the results of XML DOM traversal and canonicalization APIs in such a way that an attacker may be able to manipulate the SAML data without invalidating the cryptographic signature, allowing the attack to potentially bypass authentication to SAML service providers.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-11430
- https://duo.com/blog/duo-finds-saml-vulnerabilities-affecting-multiple-implementations
- https://github.com/omniauth/omniauth-saml
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/omniauth-saml/CVE-2017-11430.yml
- https://www.kb.cert.org/vuls/id/475445
