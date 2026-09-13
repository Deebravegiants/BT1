# [H] Omniauth allows POST parameters to be stored in session

## Summary
Severity: High
Advisory: GHSA-9pr6-grf4-x2fr
CVE: CVE-2017-18076
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-01-29
Source: https://github.com/advisories/GHSA-9pr6-grf4-x2fr
Type: github-advisory

## Affected
- RubyGems: `omniauth` — affected >=0 <1.3.2

## Details
In strategy.rb in OmniAuth before 1.3.2, the authenticity_token value is improperly protected because POST (in addition to GET) parameters are stored in the session and become available in the environment of the callback phase.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18076
- https://github.com/omniauth/omniauth/pull/867
- https://github.com/omniauth/omniauth/pull/867/commits/71866c5264122e196847a3980c43051446a03e9b
- https://bugs.debian.org/888523
- https://github.com/omniauth/omniauth
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/omniauth/CVE-2017-18076.yml
- https://www.debian.org/security/2018/dsa-4109
