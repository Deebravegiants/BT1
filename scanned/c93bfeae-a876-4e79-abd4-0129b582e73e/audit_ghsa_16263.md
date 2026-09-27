# [M] json-jwt allows bypass of identity checks via a sign/encryption confusion attack

## Summary
Severity: Medium
Advisory: GHSA-c8v6-786g-vjx6
CVE: CVE-2023-51774
Ecosystem: RubyGems
Published: 2024-02-29
Source: https://github.com/advisories/GHSA-c8v6-786g-vjx6
Type: github-advisory

## Affected
- RubyGems: `json-jwt` — affected >=1.16.0 <1.16.6
- RubyGems: `json-jwt` — affected >=0 <1.15.3.1

## Details
The json-jwt (aka JSON::JWT) gem 1.16.x before 1.16.6, 1.15.x before 1.15.3.1 for Ruby sometimes allows bypass of identity checks via a sign/encryption confusion attack. For example, JWE can sometimes be used to bypass JSON::JWT.decode.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-51774
- https://github.com/nov/json-jwt/issues/120
- https://github.com/nov/json-jwt/issues/121
- https://github.com/nov/json-jwt/commit/593ea8bcaf2629048bad8c036191f2da0a2e713c
- https://github.com/nov/json-jwt/commit/9c4d842a9465bd7960570ca326c3de79b4abc9d0
- https://github.com/P3ngu1nW/CVE_Request/blob/main/novjson-jwt.md
- https://github.com/nov/json-jwt
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/json-jwt/CVE-2023-51774.yml
