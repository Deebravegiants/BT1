# [M] Action Pack contains database-query restrictions bypass

## Summary
Severity: Medium
Advisory: GHSA-hgpp-pp89-4fgf
CVE: CVE-2012-2660
CWE: CWE-284
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-hgpp-pp89-4fgf
Type: github-advisory

## Affected
- RubyGems: `actionpack` — affected >=3.0.0.beta <3.0.13
- RubyGems: `actionpack` — affected >=3.1.0 <3.1.5
- RubyGems: `actionpack` — affected >=3.2.0 <3.2.4
- RubyGems: `actionpack` — affected >=0 <2.3.16

## Details
`actionpack/lib/action_dispatch/http/request.rb` in Ruby on Rails before 2.3.16, 3.0.x before 3.0.13, 3.1.x before 3.1.5, and 3.2.x before 3.2.4 does not properly consider differences in parameter handling between the Active Record component and the Rack interface, which allows remote attackers to bypass intended database-query restrictions and perform NULL checks via a crafted request, as demonstrated by certain `[nil]` values, a related issue to CVE-2012-2694.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-2660
- https://github.com/rails/rails/commit/61eed87ce32caf534bf1f52dd8134097b4ad9e1b
- https://github.com/rails/rails
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/actionpack/CVE-2012-2660.yml
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/activerecord/CVE-2012-2660.yml
- https://groups.google.com/g/rubyonrails-security/c/8SA-M3as7A8/m/Mr9fi9X4kNgJ
- https://groups.google.com/group/rubyonrails-security/msg/d890f8d58b5fbf32?dmode=source&output=gplain
- http://lists.opensuse.org/opensuse-security-announce/2012-08/msg00002.html
- http://lists.opensuse.org/opensuse-security-announce/2012-08/msg00014.html
- http://lists.opensuse.org/opensuse-security-announce/2012-08/msg00016.html
- http://lists.opensuse.org/opensuse-security-announce/2012-08/msg00017.html
- http://lists.opensuse.org/opensuse-updates/2012-08/msg00046.html
- http://rhn.redhat.com/errata/RHSA-2013-0154.html
