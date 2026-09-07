# [H] Kcapifony gem for Ruby places database user passwords on the command line

## Summary
Severity: High
Advisory: GHSA-6fcq-3cm2-j3j5
CVE: CVE-2014-5001
CWE: CWE-200
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-07-23
Source: https://github.com/advisories/GHSA-6fcq-3cm2-j3j5
Type: github-advisory

## Affected
- RubyGems: `kcapifony` — affected >=0

## Details
`lib/ksymfony1.rb` in the kcapifony gem 2.1.6 for Ruby places database user passwords on the (1) `mysqldump`, (2) `pg_dump`, (3) `mysql`, and (4) `psql` command lines, which allows local users to obtain sensitive information by listing the processes.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-5001
- https://github.com/Kunstmaan/kCapifony
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/kcapifony/CVE-2014-5001.yml
- http://www.openwall.com/lists/oss-security/2014/07/07/21
- http://www.openwall.com/lists/oss-security/2014/07/17/5
- http://www.vapid.dhs.org/advisories/kcapifony-2.1.6.html
