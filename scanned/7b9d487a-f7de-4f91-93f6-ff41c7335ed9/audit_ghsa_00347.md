# [C] mysql-bunuuid-rails vulnerable to SQL injection

## Summary
Severity: Critical
Advisory: GHSA-6j63-35hj-vmcg
CVE: CVE-2018-18476
CWE: CWE-89
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-30
Source: https://github.com/advisories/GHSA-6j63-35hj-vmcg
Type: github-advisory

## Affected
- RubyGems: `mysql-binuuid-rails` — affected >=0 <1.1.1

## Details
mysql-binuuid-rails 1.1.0 and earlier allows SQL Injection because it removes default string escaping for affected database columns.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-18476
- https://github.com/nedap/mysql-binuuid-rails/pull/18
- https://github.com/nedap/mysql-binuuid-rails/commit/9ae920951b46ff0163b16c55d744e89acb1036d4
- https://gist.github.com/viraptor/881276ea61e8d56bac6e28454c79f1e6
- https://github.com/nedap/mysql-binuuid-rails
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/mysql-binuuid-rails/CVE-2018-18476.yml
