# [C] bson is vulnerable to denial of service due to incorrect regex validation

## Summary
Severity: Critical
Advisory: GHSA-h6rj-8r3c-9gpj
CVE: CVE-2015-4412
CWE: CWE-400
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-03-05
Source: https://github.com/advisories/GHSA-h6rj-8r3c-9gpj
Type: github-advisory

## Affected
- RubyGems: `bson` — affected >=0 <1.12.3
- RubyGems: `bson` — affected >=2.0 <3.0.4

## Details
BSON injection vulnerability in the legal function in BSON (bson-ruby) gem before 3.0.4 for Ruby allows remote attackers to cause a denial of service (resource consumption) or inject arbitrary data via a crafted string.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-4412
- https://github.com/mongodb/bson-ruby/commit/976da329ff03ecdfca3030eb6efe3c85e6db9999
- https://bugzilla.redhat.com/show_bug.cgi?id=1229750
- https://github.com/advisories/GHSA-h6rj-8r3c-9gpj
- https://github.com/mongodb/bson-ruby
- https://github.com/mongodb/bson-ruby/compare/7446d7c6764dfda8dc4480ce16d5c023e74be5ca...28f34978a85b689a4480b4d343389bf4886522e7
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/bson/CVE-2015-4412.yml
- https://sakurity.com/blog/2015/06/04/mongo_ruby_regexp.html
- http://sakurity.com/blog/2015/06/04/mongo_ruby_regexp.html
- http://www.openwall.com/lists/oss-security/2015/06/06/3
- http://www.securityfocus.com/bid/75045
