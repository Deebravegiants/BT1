# [H] actionpack allows remote attackers to bypass intended access restrictions

## Summary
Severity: High
Advisory: GHSA-4ww3-3rxj-8v6q
CVE: CVE-2011-0449
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-4ww3-3rxj-8v6q
Type: github-advisory

## Affected
- RubyGems: `actionpack` — affected >=3.0.0 <3.0.4

## Details
`actionpack/lib/action_view/template/resolver.rb` in Ruby on Rails 3.0.x before 3.0.4, when a case-insensitive filesystem is used, does not properly implement filters associated with the list of available templates, which allows remote attackers to bypass intended access restrictions via an action name that uses an unintended case for alphabetic characters.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-0449
- https://github.com/rails/rails/commit/6f80224057803f85b3f448936aae89e742452c3b
- https://github.com/rails/rails/tree/main/actionpack
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/actionpack/CVE-2011-0449.yml
- https://web.archive.org/web/20201207190612/http://securitytracker.com/id?1025061
- http://groups.google.com/group/rubyonrails-security/msg/04345b2e84df5b4f?dmode=source&output=gplain
- http://lists.fedoraproject.org/pipermail/package-announce/2011-April/057650.html
- http://weblog.rubyonrails.org/2011/2/8/new-releases-2-3-11-and-3-0-4
