# [H] Rails possible ReDoS vulnerability in Accept header parsing in Action Dispatch

## Summary
Severity: High
Advisory: BIT-rails-2024-26142
Aliases: CVE-2024-26142, GHSA-jjhx-jhvp-74wq
Ecosystem: Bitnami
Published: 2024-12-20
Source: https://osv.dev/vulnerability/BIT-rails-2024-26142
Type: osv

## Affected
- Bitnami: `rails` — affected >=7.1.0 <7.1.4

## Details
Rails is a web-application framework. Starting in version 7.1.0, there is a possible ReDoS vulnerability in the Accept header parsing routines of Action Dispatch. This vulnerability is patched in 7.1.3.1. Ruby 3.2 has mitigations for this problem, so Rails applications using Ruby 3.2 or newer are unaffected.

## References
- https://discuss.rubyonrails.org/t/possible-redos-vulnerability-in-accept-header-parsing-in-action-dispatch/84946
- https://github.com/rails/rails/commit/b4d3bfb5ed8a5b5a90aad3a3b28860c7a931e272
- https://github.com/rails/rails/security/advisories/GHSA-jjhx-jhvp-74wq
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/actionpack/CVE-2024-26142.yml
- https://security.netapp.com/advisory/ntap-20240503-0003/
- https://nvd.nist.gov/vuln/detail/CVE-2024-26142
