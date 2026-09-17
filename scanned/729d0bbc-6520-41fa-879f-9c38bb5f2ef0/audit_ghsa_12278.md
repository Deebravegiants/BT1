# [M] Rails activerecord gem has Improper Input Validation vulnerability

## Summary
Severity: Medium
Advisory: GHSA-gjxw-5w2q-7grf
CVE: CVE-2010-3933
CWE: CWE-20
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-gjxw-5w2q-7grf
Type: github-advisory

## Affected
- RubyGems: `activerecord` — affected >=2.3.9 <2.3.10
- RubyGems: `activerecord` — affected >=3.0.0 <3.0.1

## Details
Ruby on Rails 2.3.9 and 3.0.0 does not properly handle nested attributes, which allows remote attackers to modify arbitrary records by changing the names of parameters for form inputs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-3933
- https://github.com/rails/rails/commit/2d96bccb1e8b62e3e11ca0c5d38aaa8cece889ae
- https://github.com/rails/rails/commit/96183e0f284bab27667e5a38fa6a1578eb029585
- https://github.com/rails/rails
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/activerecord/CVE-2010-3933.yml
- https://web.archive.org/web/20101129225633/http://securitytracker.com/alerts/2010/Oct/1024624.html
- https://web.archive.org/web/20111225083933/http://secunia.com/advisories/41930
- https://web.archive.org/web/20201208053819/http://securitytracker.com/id?1024624
- http://weblog.rubyonrails.org/2010/10/15/security-vulnerability-in-nested-attributes-code-in-ruby-on-rails-2-3-9-and-3-0-0
