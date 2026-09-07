# [H] Ruby-SAML Improper Authentication vulnerability

## Summary
Severity: High
Advisory: GHSA-x2fr-v8wf-8wwv
CVE: CVE-2017-11428
CWE: CWE-287
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2019-07-05
Source: https://github.com/advisories/GHSA-x2fr-v8wf-8wwv
Type: github-advisory

## Affected
- RubyGems: `ruby-saml` — affected >=0 <1.7.0

## Details
OneLogin Ruby-SAML 1.6.0 and earlier may incorrectly utilize the results of XML DOM traversal and canonicalization APIs in such a way that an attacker may be able to manipulate the SAML data without invalidating the cryptographic signature, allowing the attack to potentially bypass authentication to SAML service providers.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-11428
- https://duo.com/blog/duo-finds-saml-vulnerabilities-affecting-multiple-implementations
- https://www.kb.cert.org/vuls/id/475445
