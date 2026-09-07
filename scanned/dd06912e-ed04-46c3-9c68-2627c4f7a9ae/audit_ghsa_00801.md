# [H] PgHero gem allows CSRF

## Summary
Severity: High
Advisory: GHSA-v6fx-752r-ccp2
CVE: CVE-2020-16253
CWE: CWE-352
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2020-08-05
Source: https://github.com/advisories/GHSA-v6fx-752r-ccp2
Type: github-advisory

## Affected
- RubyGems: `pghero` — affected >=0 <2.7.0

## Details
The PgHero gem through 2.6.0 for Ruby allows CSRF. PgHero normally uses the `protect_from_forgery` method from Rails to prevent CSRF. However, this defaults to `:null_session`, which has no effect on non-session based authentication methods. Thus the ruby gem is vulnerable with non-session based authentication methods like basic authentication.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-16253
- https://github.com/ankane/pghero/issues/330
- https://github.com/ankane/pghero/commit/14b67b32fed19a30aaf9826ee72f2a29cda604e9
- https://github.com/ankane/pghero
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/pghero/CVE-2020-16253.yml
