# [M] actionpack CRLF injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-fcqf-h4h4-695m
CVE: CVE-2011-3186
CWE: CWE-94
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-fcqf-h4h4-695m
Type: github-advisory

## Affected
- RubyGems: `actionpack` — affected >=2.3.0 <2.3.13

## Details
CRLF injection vulnerability in `actionpack/lib/action_controller/response.rb` in Ruby on Rails 2.3.x before 2.3.13 allows remote attackers to inject arbitrary HTTP headers and conduct HTTP response splitting attacks via the Content-Type header.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-3186
- https://github.com/rails/rails/commit/11dafeaa7533be26441a63618be93a03869c83a9
- https://bugzilla.redhat.com/show_bug.cgi?id=732156
- https://github.com/rails/rails
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/actionpack/CVE-2011-3186.yml
- https://groups.google.com/forum/#!topic/rubyonrails-security/b_yTveAph2g
- https://web.archive.org/web/20150201000000*/http://secunia.com/advisories/45921
- http://groups.google.com/group/rubyonrails-security/msg/bbe342e43abaa78c?dmode=source&output=gplain
- http://lists.fedoraproject.org/pipermail/package-announce/2011-September/065137.html
- http://www.debian.org/security/2011/dsa-2301
- http://www.openwall.com/lists/oss-security/2011/08/17/1
- http://www.openwall.com/lists/oss-security/2011/08/19/11
- http://www.openwall.com/lists/oss-security/2011/08/20/1
- http://www.openwall.com/lists/oss-security/2011/08/22/13
- http://www.openwall.com/lists/oss-security/2011/08/22/14
- http://www.openwall.com/lists/oss-security/2011/08/22/5
