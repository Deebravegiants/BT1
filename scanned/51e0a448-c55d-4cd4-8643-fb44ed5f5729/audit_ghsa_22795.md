# [M] VladTheEnterprising allows local users to write to arbitrary files via a symlink attack

## Summary
Severity: Medium
Advisory: GHSA-x4vj-279x-qwf2
CVE: CVE-2014-4996
CWE: CWE-59
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-x4vj-279x-qwf2
Type: github-advisory

## Affected
- RubyGems: `VladTheEnterprising` — affected >=0

## Details
`lib/vlad/dba/mysql.rb` in the VladTheEnterprising gem 0.2 for Ruby allows local users to write to arbitrary files via a symlink attack on `/tmp/my.cnf.#{target_host}`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-4996
- https://exchange.xforce.ibmcloud.com/vulnerabilities/94744
- https://web.archive.org/web/20200229054941/http://www.securityfocus.com/bid/68731
- http://www.openwall.com/lists/oss-security/2014/07/07/14
- http://www.openwall.com/lists/oss-security/2014/07/17/5
- http://www.vapid.dhs.org/advisories/VladTheEnterprising-0.2.html
