# [H] codders-dataset Process Table Local Plaintext Credential Disclosure

## Summary
Severity: High
Advisory: GHSA-w9vv-fvw8-j6q3
CVE: CVE-2014-4991
CWE: CWE-200
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-w9vv-fvw8-j6q3
Type: github-advisory

## Affected
- RubyGems: `codders-dataset` — affected >=0

## Details
`lib/dataset/database/mysql.rb` and `lib/dataset/database/postgresql.rb` in the codders-dataset gem 1.3.2.1 for Ruby both place credentials on the mysqldump command line, which allows local users to obtain sensitive information by listing the process.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-4991
- https://github.com/codders/dataset
- https://github.com/codders/dataset/blob/master/lib/dataset/database/mysql.rb#L16-L27
- https://github.com/codders/dataset/blob/master/lib/dataset/database/postgresql.rb#L16-L27
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/codders-dataset/CVE-2014-4991.yml
- https://web.archive.org/web/20200229055915/https://www.securityfocus.com/bid/68733
- http://www.openwall.com/lists/oss-security/2014/07/07/8
- http://www.openwall.com/lists/oss-security/2014/07/17/5
- http://www.vapid.dhs.org/advisories/codders-dataset-1.3.2.1.html
