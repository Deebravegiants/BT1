# [H] backup-agoddard and backup_checksum have Information Exposure vulnerability

## Summary
Severity: High
Advisory: GHSA-wr5j-q359-6vr2
CVE: CVE-2014-4993
CWE: CWE-200
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-wr5j-q359-6vr2
Type: github-advisory

## Affected
- RubyGems: `backup-agoddard` — affected >=0
- RubyGems: `backup_checksum` — affected >=0

## Details
(1) `lib/backup/cli/utility.rb` in the `backup-agoddard` gem 3.0.28 and (2) `lib/backup/cli/utility.rb` in the `backup_checksum` gem 3.0.23 for Ruby place credentials on the openssl command line, which allows local users to obtain sensitive information by listing the process.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-4993
- https://github.com/agoddard/backup
- http://www.openwall.com/lists/oss-security/2014/07/07/11
- http://www.openwall.com/lists/oss-security/2014/07/07/12
- http://www.openwall.com/lists/oss-security/2014/07/17/5
- http://www.vapid.dhs.org/advisories/backup-agoddard-3.0.28.html
- http://www.vapid.dhs.org/advisories/backup_checksum-3.0.23.html
