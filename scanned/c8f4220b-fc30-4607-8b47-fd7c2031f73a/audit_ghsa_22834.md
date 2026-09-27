# [M] Chef Improper Access Control vulnerability

## Summary
Severity: Medium
Advisory: GHSA-f68m-q26r-64f6
CVE: CVE-2010-5142
CWE: CWE-284
Ecosystem: RubyGems
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-f68m-q26r-64f6
Type: github-advisory

## Affected
- RubyGems: `chef` — affected >=0 <0.9.0

## Details
`chef-server-api/app/controllers/users.rb` in the API in Chef before 0.9.0 does not require administrative privileges for the create, destroy, and update methods, which allows remote authenticated users to manage user accounts via requests to the /users URI.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-5142
- https://github.com/opscode/chef/commit/c3bb41f727fbe00e5de719d687757b24c8dcdfc8
- https://github.com/chef/chef
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/chef/CVE-2010-5142.yml
- http://tickets.opscode.com/browse/CHEF-1289
