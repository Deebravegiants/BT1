# [H] Laravel Passport: TokenGuard Authenticates Unrelated User for Client Credentials Tokens

## Summary
Severity: High
Advisory: GHSA-349c-2h2f-mxf6
CVE: CVE-2026-39976
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-349c-2h2f-mxf6
Type: github-advisory

## Affected
- Packagist: `laravel/passport` — affected >=13.0.0 <13.7.1

## Details
### Impact
Authentication Bypass for `client_credentials` tokens. the league/oauth2-server library sets the JWT sub claim to the client identifier (since there's no user). The token guard then passes this value to retrieveById() without validating it's actually a user identifier, potentially resolving an unrelated real user. Any machine-to-machine token can inadvertently authenticate as an actual user.


Usage of `EnsureClientIsResourceOwner` middleware together with `Passport::$clientUuids` set to `false`, can result in resolving the user instead, as stated in the [documentation](https://laravel.com/docs/13.x/passport#:~:text=The%20underlying%20OAuth2,client%20credentials%20token). 

> The [underlying OAuth2 server](https://oauth2.thephpleague.com/database-setup/#:~:text=Please%20note%20that,the%20bearer%20token.) sets the token's sub claim to the client's identifier for client credentials tokens. By default, Passport uses UUIDs for clients, so this cannot collide with a user's integer primary key. However, if you have set Passport::$clientUuids to false, a client credentials token may inadvertently resolve a user whose ID matches the client's ID. In such cases, using this middleware cannot guarantee that the incoming token is a client credentials token.

### Patches
Patched in v13.7.1

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_
Disallow usage of `client_credentials`. 


### References
- https://github.com/laravel/passport/issues/1900
- https://github.com/laravel/passport/pull/1901
- https://github.com/laravel/passport/pull/1902
- https://github.com/thephpleague/oauth2-server/issues/1456#issuecomment-2734989996

## References
- https://github.com/laravel/passport/security/advisories/GHSA-349c-2h2f-mxf6
- https://nvd.nist.gov/vuln/detail/CVE-2026-39976
- https://github.com/laravel/passport/issues/1900
- https://github.com/thephpleague/oauth2-server/issues/1456#issuecomment-2734989996
- https://github.com/laravel/passport/pull/1901
- https://github.com/laravel/passport/pull/1902
- https://github.com/laravel/passport
