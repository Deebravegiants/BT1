# [M] Authlogic Information Exposure vulnerability

## Summary
Severity: Medium
Advisory: GHSA-rx7j-mw4c-76g9
CVE: CVE-2012-6497
CWE: CWE-200
Ecosystem: RubyGems
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-rx7j-mw4c-76g9
Type: github-advisory

## Affected
- RubyGems: `authlogic` — affected >=0 <3.3.0

## Details
The Authlogic gem for Ruby on Rails prior to version 3.3.0 makes potentially unsafe `find_by_id` method calls, which might allow remote attackers to conduct CVE-2012-6496 SQL injection attacks via a crafted parameter in environments that have a known secret_token value, as demonstrated by a value contained in `secret_token.rb` in an open-source product.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-6497
- https://github.com/binarylogic/authlogic/pull/341
- https://github.com/binarylogic/authlogic/commit/1d57a6c4abe43a3c0b4ef578486ea00e1f7a9873
- https://github.com/binarylogic/authlogic
- https://web.archive.org/web/20130104161608/http://www.securityfocus.com/bid/57084
- https://web.archive.org/web/20130116043311/http://phenoelit.org/blog/archives/2012/12/21/let_me_github_that_for_you/index.html
- http://blog.phusion.nl/2013/01/03/rails-sql-injection-vulnerability-hold-your-horses-here-are-the-facts
- http://openwall.com/lists/oss-security/2013/01/03/12
