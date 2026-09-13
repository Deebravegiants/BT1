# [C] Active Record contains deserialization of arbitrary YAML

## Summary
Severity: Critical
Advisory: GHSA-fhj9-cjjh-27vm
CVE: CVE-2013-0277
CWE: CWE-502
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-fhj9-cjjh-27vm
Type: github-advisory

## Affected
- RubyGems: `activerecord` — affected >=0 <2.3.17
- RubyGems: `activerecord` — affected >=3.0.0 <3.1.0

## Details
ActiveRecord in Ruby on Rails before 2.3.17 and 3.x before 3.1.0 allows remote attackers to cause a denial of service or execute arbitrary code via crafted serialized attributes that cause the +serialize+ helper to deserialize arbitrary YAML.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-0277
- https://github.com/rails/rails/tree/v6.1.4.1/activerecord
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/activerecord/CVE-2013-0277.yml
- https://groups.google.com/group/rubyonrails-security/msg/302ec7ce90f13837?dmode=source&output=gplain
- https://puppet.com/security/cve/cve-2013-0277
- http://lists.apple.com/archives/security-announce/2013/Jun/msg00000.html
- http://lists.opensuse.org/opensuse-updates/2013-03/msg00048.html
- http://securitytracker.com/id?1028109
- http://support.apple.com/kb/HT5784
- http://weblog.rubyonrails.org/2013/2/11/SEC-ANN-Rails-3-2-12-3-1-11-and-2-3-17-have-been-released
- http://www.debian.org/security/2013/dsa-2620
- http://www.openwall.com/lists/oss-security/2013/02/11/6
