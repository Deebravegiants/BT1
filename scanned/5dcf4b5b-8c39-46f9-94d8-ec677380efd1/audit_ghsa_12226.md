# [H] Dragonfly Code Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-p463-639r-q9g9
CVE: CVE-2013-1756
CWE: CWE-94
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-p463-639r-q9g9
Type: github-advisory

## Affected
- RubyGems: `dragonfly` — affected >=0.7 <0.8.6
- RubyGems: `dragonfly` — affected >=0.9 <0.9.13

## Details
The Dragonfly gem 0.7 before 0.8.6 and 0.9.x before 0.9.13 for Ruby, when used with Ruby on Rails, allows remote attackers to execute arbitrary code via a crafted request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-1756
- https://github.com/markevans/dragonfly/commit/a8775aacf9e5c81cf11bec34b7afa7f27ddfe277
- https://exchange.xforce.ibmcloud.com/vulnerabilities/82476
- https://github.com/markevans/dragonfly
- https://groups.google.com/forum/?fromgroups=#!topic/dragonfly-users/3c3WIU3VQTo
- https://web.archive.org/web/20200229103538/http://www.securityfocus.com/bid/58225
