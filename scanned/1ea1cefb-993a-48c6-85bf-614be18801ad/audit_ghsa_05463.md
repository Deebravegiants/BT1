# [H] ActiveRecord-JDBC-Adapter (AR-JDBC) lib/arjdbc/jdbc/adapter.rb sql.gsub() Function SQL Injection

## Summary
Severity: High
Advisory: GHSA-5qw5-wf2q-f538
CWE: CWE-89
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-01-16
Source: https://github.com/advisories/GHSA-5qw5-wf2q-f538
Type: github-advisory

## Affected
- RubyGems: `activerecord-jdbc-adapter` — affected >=0 <1.2.8

## Details
ActiveRecord-JDBC-Adapter (AR-JDBC) contains a flaw that may allow carrying out an SQL injection attack. The issue is due to the sql.gsub() function in lib/arjdbc/jdbc/adapter.rb not properly sanitizing user-supplied input before using it in SQL queries. This may allow a remote attacker to inject or manipulate SQL queries in the back-end database, allowing for the manipulation or disclosure of arbitrary data.

## References
- https://github.com/jruby/activerecord-jdbc-adapter/issues/322
- https://github.com/jruby/activerecord-jdbc-adapter
- https://github.com/jruby/activerecord-jdbc-adapter/blob/master/lib/arjdbc/jdbc/adapter.rb
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/activerecord-jdbc-adapter/GHSA-5qw5-wf2q-f538.yml
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/activerecord-jdbc-adapter/OSVDB-114854.yml
