# [M] rails is vulnerable to CRLF injection

## Summary
Severity: Medium
Advisory: GHSA-jmgf-p46x-982h
CVE: CVE-2008-5189
CWE: CWE-352
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-jmgf-p46x-982h
Type: github-advisory

## Affected
- RubyGems: `rails` — affected >=0 <2.0.5

## Details
CRLF injection vulnerability in Ruby on Rails before 2.0.5 allows remote attackers to inject arbitrary HTTP headers and conduct HTTP response splitting attacks via a crafted URL to the redirect_to function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2008-5189
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rails/CVE-2008-5189.yml
- http://github.com/rails/rails
- http://github.com/rails/rails/commit/7282ed863ca7e6f928bae9162c9a63a98775a19d
- http://lists.opensuse.org/opensuse-security-announce/2008-12/msg00002.html
- http://weblog.rubyonrails.org/2008/10/19/rails-2-0-5-redirect_to-and-offset-limit-sanitizing
- http://weblog.rubyonrails.org/2008/10/19/response-splitting-risk
