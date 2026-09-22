# [M] activesupport Improper Input Validation vulnerability

## Summary
Severity: Medium
Advisory: GHSA-9c2j-593q-3g82
CVE: CVE-2013-1856
CWE: CWE-20
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-9c2j-593q-3g82
Type: github-advisory

## Affected
- RubyGems: `activesupport` — affected >=3.0.0 <3.1.12
- RubyGems: `activesupport` — affected >=3.2.0 <3.2.13

## Details
The `ActiveSupport::XmlMini_JDOM` backend in `lib/active_support/xml_mini/jdom.rb` in the Active Support component in Ruby on Rails 3.0.x and 3.1.x before 3.1.12 and 3.2.x before 3.2.13, when JRuby is used, does not properly restrict the capabilities of the XML parser, which allows remote attackers to read arbitrary files or cause a denial of service (resource consumption) via vectors involving (1) an external DTD or (2) an external entity declaration in conjunction with an entity reference.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-1856
- https://github.com/rails/rails
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/activesupport/CVE-2013-1856.yml
- https://groups.google.com/group/rubyonrails-security/msg/6c2482d4ed1545e6?dmode=source&output=gplain
- https://web.archive.org/web/20130609174600/http://lists.apple.com/archives/security-announce/2013/Jun/msg00000.html
- https://web.archive.org/web/20131109010518/http://lists.apple.com/archives/security-announce/2013/Oct/msg00006.html
- http://lists.apple.com/archives/security-announce/2013/Jun/msg00000.html
- http://lists.apple.com/archives/security-announce/2013/Oct/msg00006.html
- http://support.apple.com/kb/HT5784
- http://weblog.rubyonrails.org/2013/3/18/SEC-ANN-Rails-3-2-13-3-1-12-and-2-3-18-have-been-released
