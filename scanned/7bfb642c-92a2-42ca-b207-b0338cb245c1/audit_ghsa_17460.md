# [C] Ruby-saml has a SAML authentication bypass due to namespace handling (parser differential)

## Summary
Severity: Critical
Advisory: GHSA-9v8j-x534-2fx3
CVE: CVE-2025-66567
CWE: CWE-347
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-12-08
Source: https://github.com/advisories/GHSA-9v8j-x534-2fx3
Type: github-advisory

## Affected
- RubyGems: `ruby-saml` — affected >=0 <1.18.0

## Details
### Summary

Ruby-saml up to and including 1.12.4, there is an authentication bypass vulnerability because of an incomplete fix for CVE-2025-25292. ReXML and Nokogiri parse XML differently, the parsers can generate entirely different document structures from the same XML input. That allows an attacker to be able to execute a Signature Wrapping attack. The vulnerability does not affect the version 1.18.0.

### Impact
That allows an attacker to be able to execute a Signature Wrapping attack and bypass the authentication

## References
- https://github.com/SAML-Toolkits/ruby-saml/security/advisories/GHSA-9v8j-x534-2fx3
- https://nvd.nist.gov/vuln/detail/CVE-2025-66567
- https://github.com/SAML-Toolkits/ruby-saml/commit/e9c1cdbd0f9afa467b585de279db0cbd0fb8ae97
- https://github.com/SAML-Toolkits/ruby-saml
- https://github.com/advisories/GHSA-754f-8gm6-c4r2
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/ruby-saml/CVE-2025-66567.yml
