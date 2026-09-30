# [H] eZ Platform CSRF token in login form is disabled by default

## Summary
Severity: High
Advisory: GHSA-45qm-j4m9-whv9
CWE: CWE-352
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-45qm-j4m9-whv9
Type: github-advisory

## Affected
- Packagist: `ezsystems/ezplatform` — affected >=2.5.0 <2.5.4

## Details
his security advisory fixes a potential vulnerability in the eZ Platform log in form. That form has a Cross-Site Request Forgery (CSRF) token, but the CSRF functionality is not enabled by default, meaning the token is inactive. The fix is distributed via Composer as ezsystems/ezplatform v2.5.4, and in v3.0.0 when that will be released.

If you'd like to manually enable it in your configuration, this is done by editing your app/config/security.yml and setting the "csrf_token_generator" key to "security.csrf.token_manager", like this:
```
security:
    firewalls:
        ezpublish_front:
            form_login:
                csrf_token_generator: security.csrf.token_manager
```
NB: In eZ Platform 3.0 this file has been moved to config/packages/security.yaml

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/ezsystems/ezplatform/2019-06-27-1.yaml
- https://github.com/ezsystems/ezplatform
- https://share.ez.no/community-project/security-advisories/ezsa-2019-004-csrf-token-in-login-form-is-disabled-by-default
- https://web.archive.org/web/20210614185223/https://share.ez.no/community-project/security-advisories/ezsa-2019-004-csrf-token-in-login-form-is-disabled-by-default
