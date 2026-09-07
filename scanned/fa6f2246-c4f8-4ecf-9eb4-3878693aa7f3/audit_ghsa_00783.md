# [M] Field Test CSRF vulnerability

## Summary
Severity: Medium
Advisory: GHSA-w542-cpp9-r3g7
CVE: CVE-2020-16252
CWE: CWE-352
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2020-08-05
Source: https://github.com/advisories/GHSA-w542-cpp9-r3g7
Type: github-advisory

## Affected
- RubyGems: `field_test` — affected >=0.2.0 <0.4.0

## Details
The Field Test dashboard is vulnerable to cross-site request forgery (CSRF) with non-session based authentication methods in versions v0.2.0 through v0.3.2.

## Impact
The Field Test dashboard is vulnerable to CSRF with non-session based authentication methods, like basic authentication. Session-based authentication methods (like Devise's default authentication) are not affected.

A CSRF attack works by getting an authorized user to visit a malicious website and then performing requests on behalf of the user. In this instance, a single endpoint is affected, which allows for changing the variant assigned to a user.

All users running an affected release should upgrade immediately.

## Technical Details
Field Test uses the `protect_from_forgery` method from Rails to prevent CSRF. However, this defaults to `:null_session`, which has no effect on non-session based authentication methods. This has been changed to `protect_from_forgery with: :exception`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-16252
- https://github.com/ankane/field_test/issues/28
- https://github.com/ankane/field_test/commit/defd3fdf457c22d7dc5b3be7048481947bd5f0d0
- https://github.com/ankane/field_test
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/field_test/CVE-2020-16252.yml
