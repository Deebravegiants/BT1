# [H] brbackup exposes database password to unauthorized users

## Summary
Severity: High
Advisory: GHSA-vqcm-7f7f-r539
CVE: CVE-2014-5004
CWE: CWE-200
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-03-05
Source: https://github.com/advisories/GHSA-vqcm-7f7f-r539
Type: github-advisory

## Affected
- RubyGems: `brbackup` — affected 0.1.1

## Details
lib/brbackup.rb in the brbackup gem 0.1.1 for Ruby places the database password on the mysql command line, which allows local users to obtain sensitive information by listing the process.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-5004
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/brbackup/CVE-2014-5004.yml
- https://web.archive.org/web/20200229054738/http://www.securityfocus.com/bid/68506
- http://www.openwall.com/lists/oss-security/2014/07/10/6
- http://www.openwall.com/lists/oss-security/2014/07/17/5
- http://www.vapid.dhs.org/advisories/brbackup-0.1.1.html
