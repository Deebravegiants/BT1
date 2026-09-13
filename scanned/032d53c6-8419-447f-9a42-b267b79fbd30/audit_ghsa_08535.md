# [H] ruby-jwt: Empty-key HMAC bypass; cross-language sibling of CVE-2026-44351

## Summary
Severity: High
Advisory: GHSA-c32j-vqhx-rx3x
CVE: CVE-2026-45363
CWE: CWE-1391, CWE-287, CWE-326
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-c32j-vqhx-rx3x
Type: github-advisory

## Affected
- RubyGems: `jwt` — affected >=3.0.0 <3.2.0
- RubyGems: `jwt` — affected >=0 <2.10.3

## Details
`JWT.decode(token, '', true, algorithm: 'HS256')` accepts an attacker-forged token.
`OpenSSL::HMAC.digest('SHA256', '', payload)` returns a valid digest under an empty key, and no `raise
  InvalidKeyError if key.empty?` precondition exists in the HMAC algorithm.

```
JWT.decode(token, "", true, algorithm: 'HS256')
  -> JWA::Hmac.verify(verification_key: "", ...)
  -> OpenSSL::HMAC.digest('SHA256', "", signing_input) == signature
```

The same path is reached when a keyfinder block or key_finder: argument returns "", nil, or an
array containing nil for an unknown key. JWT::Decode#find_key only rejects literal nil and empty
arrays, and JWT::JWA::Hmac silently coerces nil to "" (signing_key ||= '') before signing.

```
JWT.decode(token, nil, true, algorithms: ['HS256']) { |_h| "" }
  -> find_key returns ""               # "" && !Array("").empty? == true
  -> JWA::Hmac.verify(verification_key: "", ...)
  -> verifies
```
Common application patterns that produce the unsafe value: `redis.get("kid:#{kid}").to_s`, ORM string columns with `default: ''`, `ENV['SECRET'] || '', Hash.new('')` lookups, [primary, fallback] where fallback may be nil. Applications passing a non-empty static key:, or whose keyfinder returns nil / raises on miss, are not affected.

The existing `enforce_hmac_key_length` option would block this but defaults to false. On OpenSSL ≥ 3.5 the empty-key HMAC.digest call no longer raises, so the OpenSSL-3.0 rescue in JWA::Hmac#sign does not fire.

Affects HS256/HS384/HS512 via both JWT.decode (positional key and block keyfinder) and
`JWT::EncodedToken#verify_signature!(key_finder:)`

## References
- https://github.com/jwt/ruby-jwt/security/advisories/GHSA-c32j-vqhx-rx3x
- https://github.com/jwt/ruby-jwt/issues/724
- https://github.com/jwt/ruby-jwt/commit/db560b769a07bd9724e77ff505011ac01872106f
- https://github.com/jwt/ruby-jwt
- https://github.com/jwt/ruby-jwt/releases/tag/v2.10.3
- https://github.com/jwt/ruby-jwt/releases/tag/v3.2.0
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/jwt/CVE-2026-45363.yml
- https://www.cve.org/CVERecord?id=CVE-2026-45363
