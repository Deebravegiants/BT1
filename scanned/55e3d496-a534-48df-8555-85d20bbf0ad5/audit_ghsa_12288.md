# [M] Directory traversal vulnerability in actionpack

## Summary
Severity: Medium
Advisory: GHSA-h56m-vwxc-3qpw
CVE: CVE-2014-7829
CWE: CWE-22
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-h56m-vwxc-3qpw
Type: github-advisory

## Affected
- RubyGems: `actionpack` — affected >=4.1.0 <4.1.8
- RubyGems: `actionpack` — affected >=3.0.0 <3.2.21
- RubyGems: `actionpack` — affected >=4.0.0 <4.0.12
- RubyGems: `actionpack` — affected >=4.2.0.beta1 <4.2.0.beta4

## Details
Directory traversal vulnerability in actionpack/lib/action_dispatch/middleware/static.rb in Action Pack in Ruby on Rails 3.x before 3.2.21, 4.0.x before 4.0.12, 4.1.x before 4.1.8, and 4.2.x before 4.2.0.beta4, when serve_static_assets is enabled, allows remote attackers to determine the existence of files outside the application root via vectors involving a \ (backslash) character, a similar issue to CVE-2014-7818.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-7829
- https://github.com/advisories/GHSA-h56m-vwxc-3qpw
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/actionpack/CVE-2014-7829.yml
- https://groups.google.com/forum/#!topic/rubyonrails-security/rMTQy4oRCGk
- https://groups.google.com/forum/message/raw?msg=rubyonrails-security/rMTQy4oRCGk/loS_CRS8mNEJ
- https://puppet.com/security/cve/cve-2014-7829
- https://web.archive.org/web/20160403085126/http://www.securityfocus.com/bid/71183
- http://lists.opensuse.org/opensuse-updates/2014-11/msg00112.html
