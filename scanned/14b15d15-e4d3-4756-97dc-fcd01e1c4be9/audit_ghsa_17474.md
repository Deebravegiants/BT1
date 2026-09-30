# [C] Ruby-saml allows a Libxml2 Canonicalization error to bypass Digest/Signature validation

## Summary
Severity: Critical
Advisory: GHSA-x4h9-gwv3-r4m4
CVE: CVE-2025-66568
CWE: CWE-347
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-12-08
Source: https://github.com/advisories/GHSA-x4h9-gwv3-r4m4
Type: github-advisory

## Affected
- RubyGems: `ruby-saml` — affected >=0 <1.18.0

## Details
### Summary
Ruby-saml up to and including 1.12.4, there is an authentication bypass vulnerability because of an issue at libxml2 canonicalization process used by Nokogiri for document transformation. That allows an attacker to be able to execute a Signature Wrapping attack. The vulnerability does not affect the version 1.18.0.

### Details
When libxml2’s canonicalization is invoked on an invalid XML input, it may return an empty string rather than a canonicalized node. ruby-saml then proceeds to compute the DigestValue over this empty string, treating it as if canonicalization succeeded.

### Impact
1. Digest bypass: By crafting input that causes canonicalization to yield an empty string, the attacker can manipulate validation to pass incorrectly.

2. Signature replay on empty canonical form: If an empty string has been signed once (e.g., in a prior interaction or via a misconfigured flow), that signature can potentially be replayed to bypass authentication.

## References
- https://github.com/SAML-Toolkits/ruby-saml/security/advisories/GHSA-x4h9-gwv3-r4m4
- https://nvd.nist.gov/vuln/detail/CVE-2025-66568
- https://github.com/SAML-Toolkits/ruby-saml/commit/acac9e9cc0b9a507882c614f25d41f8b47be349a
- https://github.com/SAML-Toolkits/ruby-saml
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/ruby-saml/CVE-2025-66568.yml
