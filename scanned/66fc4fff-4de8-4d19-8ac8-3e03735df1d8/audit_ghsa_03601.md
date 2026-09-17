# [H] Prototype Pollution in chartkick

## Summary
Severity: High
Advisory: GHSA-5pm8-492c-92p5
CVE: CVE-2019-18841
Ecosystem: RubyGems, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2019-12-02
Source: https://github.com/advisories/GHSA-5pm8-492c-92p5
Type: github-advisory

## Affected
- RubyGems: `chartkick` — affected >=0 <3.3.0
- npm: `chartkick` — affected >=3.1.0 <3.2.0

## Details
Affected versions of `@polymer/polymer` are vulnerable to prototype pollution. The package fails to prevent modification of object prototypes through chart options containing a payload such as `{"__proto__": {"polluted": true}}`. It is possible to achieve the same results if a chart loads data from a malicious server.


## Recommendation

Upgrade to version 3.2.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-18841
- https://github.com/ankane/chartkick.js/issues/117
- https://github.com/ankane/chartkick/commit/b810936bbf687bc74c5b6dba72d2397a399885fa
- https://chartkick.com
- https://github.com/ankane/chartkick/blob/master/CHANGELOG.md
- https://github.com/ankane/chartkick/commits/master
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/chartkick/CVE-2019-18841.yml
- https://rubygems.org/gems/chartkick
