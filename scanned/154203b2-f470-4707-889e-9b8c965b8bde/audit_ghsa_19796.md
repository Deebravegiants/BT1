# [C] omniauth-saml has dependency on ruby-saml version with Signature Wrapping Attack issue

## Summary
Severity: Critical
Advisory: GHSA-hw46-3hmr-x9xv
CWE: CWE-347
Ecosystem: RubyGems
Published: 2025-03-12
Source: https://github.com/advisories/GHSA-hw46-3hmr-x9xv
Type: github-advisory

## Affected
- RubyGems: `omniauth-saml` — affected >=2.2.0 <2.2.3
- RubyGems: `omniauth-saml` — affected >=2.0.0 <2.1.3
- RubyGems: `omniauth-saml` — affected >=0 <1.10.6

## Details
### Summary
There are 2 new Critical Signature Wrapping Vulnerabilities (CVE-2025-25292, CVE-2025-25291) and a potential DDOS Moderated Vulneratiblity (CVE-2025-25293) affecting ruby-saml, a dependency of omniauth-saml.

The fix will be applied to ruby-saml and released 12 March 2025, under version 1.18.0.

Please [upgrade](https://github.com/omniauth/omniauth-saml/blob/master/omniauth-saml.gemspec#L16) the ruby-saml requirement to v1.18.0.

### Impact
Signature Wrapping Vulnerabilities allows an attacker to impersonate a user.

## References
- https://github.com/omniauth/omniauth-saml/security/advisories/GHSA-hw46-3hmr-x9xv
- https://github.com/omniauth/omniauth-saml/commit/0d5eaa0d808acb2ac96deadf5c750ac1cf2d92b5
- https://github.com/omniauth/omniauth-saml/commit/2c8a482801808bbcb0188214bde74680b8018a35
- https://github.com/omniauth/omniauth-saml/commit/7a348b49083462a566af41a5ae85e9f3af15b985
- https://github.com/omniauth/omniauth-saml
- https://github.com/omniauth/omniauth-saml/blob/master/omniauth-saml.gemspec#L16
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/omniauth-saml/GHSA-hw46-3hmr-x9xv.yml
- https://rubygems.org/gems/omniauth-saml/versions/2.2.3
