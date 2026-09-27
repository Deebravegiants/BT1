# [M] actionpack vulnerable to Path Traversal

## Summary
Severity: Medium
Advisory: GHSA-29gr-w57f-rpfw
CVE: CVE-2014-7818
CWE: CWE-22
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-29gr-w57f-rpfw
Type: github-advisory

## Affected
- RubyGems: `actionpack` — affected >=3.0.0 <3.2.20
- RubyGems: `actionpack` — affected >=4.0.0 <4.0.11
- RubyGems: `actionpack` — affected >=4.1.0 <4.1.7
- RubyGems: `actionpack` — affected >=4.2.0.beta1 <4.2.0.beta3

## Details
Directory traversal vulnerability in `actionpack/lib/action_dispatch/middleware/static.rb` in Action Pack in Ruby on Rails 3.x before 3.2.20, 4.0.x before 4.0.11, 4.1.x before 4.1.7, and 4.2.x before 4.2.0.beta3, when `serve_static_assets` is enabled, allows remote attackers to determine the existence of files outside the application root via a `/..%2F` sequence.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-7818
- https://github.com/advisories/GHSA-29gr-w57f-rpfw
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/actionpack/CVE-2014-7818.yml
- https://groups.google.com/forum/#!topic/rubyonrails-security/dCp7duBiQgo
- https://groups.google.com/forum/message/raw?msg=rubyonrails-security/dCp7duBiQgo/v_R_8PFs5IwJ
- https://puppet.com/security/cve/cve-2014-7829
- http://lists.opensuse.org/opensuse-updates/2014-11/msg00112.html
