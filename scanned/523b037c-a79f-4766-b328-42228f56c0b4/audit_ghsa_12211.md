# [M] Denial of service in ruby-openid

## Summary
Severity: Medium
Advisory: GHSA-6c8p-qphv-668v
CVE: CVE-2013-1812
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-6c8p-qphv-668v
Type: github-advisory

## Affected
- RubyGems: `ruby-openid` — affected >=0 <2.2.2

## Details
The ruby-openid gem before 2.2.2 for Ruby allows remote OpenID providers to cause a denial of service (CPU consumption) via (1) a large XRDS document or (2) an XML Entity Expansion (XEE) attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-1812
- https://github.com/openid/ruby-openid/pull/43
- https://github.com/openid/ruby-openid/commit/a3693cef06049563f5b4e4824f4d3211288508ed
- https://bugzilla.redhat.com/show_bug.cgi?id=918134
- https://github.com/advisories/GHSA-6c8p-qphv-668v
- https://github.com/openid/ruby-openid
- https://github.com/openid/ruby-openid/blob/master/CHANGELOG.md
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/ruby-openid/CVE-2013-1812.yml
- http://lists.fedoraproject.org/pipermail/package-announce/2013-November/120204.html
- http://lists.fedoraproject.org/pipermail/package-announce/2013-November/120361.html
- http://www.openwall.com/lists/oss-security/2013/03/03/8
