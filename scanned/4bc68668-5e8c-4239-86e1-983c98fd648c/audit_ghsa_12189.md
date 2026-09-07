# [M] activesupport Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-qv8p-v9qw-wc7g
CVE: CVE-2012-1098
CWE: CWE-79
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-qv8p-v9qw-wc7g
Type: github-advisory

## Affected
- RubyGems: `activesupport` — affected >=3.0.0 <3.0.12
- RubyGems: `activesupport` — affected >=3.1.0 <3.1.4
- RubyGems: `activesupport` — affected >=3.2.0 <3.2.2

## Details
Cross-site scripting (XSS) vulnerability in Ruby on Rails 3.0.x before 3.0.12, 3.1.x before 3.1.4, and 3.2.x before 3.2.2 allows remote attackers to inject arbitrary web script or HTML via vectors involving a SafeBuffer object that is manipulated through certain methods.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-1098
- https://bugzilla.redhat.com/show_bug.cgi?id=799275
- http://groups.google.com/group/rubyonrails-security/msg/1c2e01a5e42722c9?dmode=source&output=gplain
- http://lists.fedoraproject.org/pipermail/package-announce/2012-March/075675.html
- http://weblog.rubyonrails.org/2012/3/1/ann-rails-3-0-12-has-been-released
- http://www.openwall.com/lists/oss-security/2012/03/02/6
- http://www.openwall.com/lists/oss-security/2012/03/03/1
