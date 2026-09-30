# [H] kajam allows local users to obtain sensitive information by listing the process

## Summary
Severity: High
Advisory: GHSA-4ph7-5c44-pppv
CVE: CVE-2014-4999
CWE: CWE-200
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-4ph7-5c44-pppv
Type: github-advisory

## Affected
- RubyGems: `kajam` — affected >=0

## Details
`vendor/plugins/dataset/lib/dataset/database/mysql.rb` in the kajam gem 1.0.3.rc2 for Ruby places the mysql user password on the (1) mysqldump command line in the capture function and (2) mysql command line in the restore function, which allows local users to obtain sensitive information by listing the process.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-4999
- http://www.openwall.com/lists/oss-security/2014/07/07/19
- http://www.openwall.com/lists/oss-security/2014/07/17/5
- http://www.vapid.dhs.org/advisories/kajam-1.0.3.rc2.html
