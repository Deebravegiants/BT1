# [H] Denial of Service in jquery

## Summary
Severity: High
Advisory: GHSA-mhpp-875w-9cpv
CVE: CVE-2016-10707
CWE: CWE-400, CWE-674
Ecosystem: Maven, NuGet, RubyGems, npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-01-22
Source: https://github.com/advisories/GHSA-mhpp-875w-9cpv
Type: github-advisory

## Affected
- npm: `jquery` — affected >=3.0.0-rc.1 <3.0.0
- NuGet: `jQuery` — affected >=3.0.0-rc.1 <3.0.0
- Maven: `org.webjars.npm:jquery` — affected >=3.0.0-rc1 <3.0.0
- RubyGems: `jquery-rails` — affected >=3.0.0-rc.1 <3.0.0

## Details
Affected versions of `jquery` use a lowercasing logic on attribute names. When given a boolean attribute with a name that contains uppercase characters, `jquery` enters into an infinite recursion loop, exceeding the call stack limit, and resulting in a denial of service condition.


## Recommendation

Update to version 3.0.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10707
- https://github.com/jquery/jquery/issues/3133
- https://github.com/jquery/jquery/issues/3133#issuecomment-358978489
- https://github.com/jquery/jquery/pull/3134
- https://github.com/advisories/GHSA-mhpp-875w-9cpv
- https://github.com/jquery/jquery
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/jquery-rails/CVE-2016-10707.yml
- https://snyk.io/vuln/npm:jquery:20160529
- https://www.npmjs.com/advisories/330
