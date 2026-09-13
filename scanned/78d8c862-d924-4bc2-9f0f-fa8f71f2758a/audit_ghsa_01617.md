# [H] Regression in JWT Signature Validation

## Summary
Severity: High
Advisory: GHSA-58r4-h6v8-jcvm
CVE: CVE-2020-15240
CWE: CWE-287, CWE-347
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2020-11-03
Source: https://github.com/advisories/GHSA-58r4-h6v8-jcvm
Type: github-advisory

## Affected
- RubyGems: `omniauth-auth0` — affected >=2.3.0 <2.4.1

## Details
### Overview
Versions after and including `2.3.0` are improperly validating the JWT token signature when using the `JWTValidator.verify` method.  Improper validation of the JWT token signature when not using the default Authorization Code Flow can allow an attacker to bypass authentication and authorization.

### Am I affected?
You are affected by this vulnerability if all of the following conditions apply:

- You are using `omniauth-auth0`.
- You are using `JWTValidator.verify` method directly OR you are not authenticating using the SDK’s default Authorization Code Flow.

### How to fix that?
Upgrade to version `2.4.1`.

### Will this update impact my users?
The fix provided in this version will not affect your users.

## References
- https://github.com/auth0/omniauth-auth0/security/advisories/GHSA-58r4-h6v8-jcvm
- https://nvd.nist.gov/vuln/detail/CVE-2020-15240
- https://github.com/auth0/omniauth-auth0/commit/fd3a14f4ccdfbc515d1121d6378ff88bf55a7a7a
- https://github.com/auth0/omniauth-auth0
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/omniauth-auth0/CVE-2020-15240.yml
- https://rubygems.org/gems/omniauth-auth0
