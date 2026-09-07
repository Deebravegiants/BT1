# [M] session fixation protection mechanism in cgi_process.rb in Rails

## Summary
Severity: Medium
Advisory: GHSA-p4c6-77gc-694x
CVE: CVE-2007-6077
CWE: CWE-362
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-p4c6-77gc-694x
Type: github-advisory

## Affected
- RubyGems: `rails` — affected >=0 <1.2.6

## Details
The session fixation protection mechanism in cgi_process.rb in Rails 1.2.4, as used in Ruby on Rails, removes the :cookie_only attribute from the DEFAULT_SESSION_OPTIONS constant, which effectively causes cookie_only to be applied only to the first instantiation of CgiRequest, which allows remote attackers to conduct session fixation attacks.  NOTE: this is due to an incomplete fix for CVE-2007-5380.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2007-6077
- https://github.com/advisories/GHSA-p4c6-77gc-694x
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rails/CVE-2007-6077.yml
- https://rubyonrails.org/2007/11/24/ruby-on-rails-1-2-6-security-and-maintenance-release
- http://dev.rubyonrails.org/changeset/8177
- http://dev.rubyonrails.org/ticket/10048
- http://docs.info.apple.com/article.html?artnum=307179
- http://lists.apple.com/archives/security-announce/2007/Dec/msg00002.html
- http://secunia.com/advisories/27781
- http://secunia.com/advisories/28136
- http://weblog.rubyonrails.org/2007/11/24/ruby-on-rails-1-2-6-security-and-maintenance-release
- http://www.securityfocus.com/bid/26598
- http://www.us-cert.gov/cas/techalerts/TA07-352A.html
- http://www.vupen.com/english/advisories/2007/4009
- http://www.vupen.com/english/advisories/2007/4238
