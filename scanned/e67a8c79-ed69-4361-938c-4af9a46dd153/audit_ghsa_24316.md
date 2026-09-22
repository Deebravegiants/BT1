# [M] spree_auth_devise allows remote authenticated users to assign themselves arbitrary roles

## Summary
Severity: Medium
Advisory: GHSA-jp57-9j37-5476
CVE: CVE-2013-2506
Ecosystem: RubyGems
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-jp57-9j37-5476
Type: github-advisory

## Affected
- RubyGems: `spree_auth_devise` — affected >=1.0.0 <3.0.5

## Details
`app/models/spree/user.rb` in spree_auth_devise in Spree 1.1.x before 1.1.6, 1.2.x, and 1.3.x does not perform mass assignment safely when updating a user, which allows remote authenticated users to assign arbitrary roles to themselves.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-2506
- https://github.com/spree/spree_auth_devise/commit/038d74771d3b5c13d13b738b73dfda1033a99f65
- https://github.com/spree/spree_auth_devise/commit/fda3ab9fb536c64fe18a9b78bb21c6176b3ea24d
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/spree_auth/CVE-2013-2506.yml
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/spree_auth_devise/CVE-2013-2506.yml
- https://github.com/spree/spree_auth_devise
- https://web.archive.org/web/20131207040639/https://rubygems.org/gems/spree_auth_devise/versions
- https://web.archive.org/web/20160331131233/https://spreecommerce.com/blog/multiple-security-vulnerabilities-fixed
