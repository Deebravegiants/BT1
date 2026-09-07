# [H] Cross-site request forgery in rails_admin

## Summary
Severity: High
Advisory: GHSA-pxqr-8v54-m2hj
CVE: CVE-2016-10522
CWE: CWE-352
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-08-08
Source: https://github.com/advisories/GHSA-pxqr-8v54-m2hj
Type: github-advisory

## Affected
- RubyGems: `rails_admin` — affected >=1.0.0 <1.1.1

## Details
rails_admin ruby gem <v1.1.1 is vulnerable to cross-site request forgery (CSRF) attacks. Non-GET methods were not validating CSRF tokens and, as a result, an attacker could hypothetically gain access to the application administrative endpoints exposed by the gem.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10522
- https://github.com/railsadminteam/rails_admin/commit/b13e879eb93b661204e9fb5e55f7afa4f397537a
- https://github.com/advisories/GHSA-pxqr-8v54-m2hj
- https://github.com/railsadminteam/rails_admin
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rails_admin/CVE-2016-10522.yml
- https://www.sourceclear.com/registry/security/cross-site-request-forgery-csrf-/ruby/sid-3173
