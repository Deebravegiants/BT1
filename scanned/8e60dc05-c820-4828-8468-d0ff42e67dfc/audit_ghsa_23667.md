# [H] VladTheEnterprising allows local users to obtain sensitive information by reading MySQL root password from temporary file

## Summary
Severity: High
Advisory: GHSA-86cf-g34f-7462
CVE: CVE-2014-4995
CWE: CWE-200
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-86cf-g34f-7462
Type: github-advisory

## Affected
- RubyGems: `VladTheEnterprising` — affected >=0

## Details
Race condition in `lib/vlad/dba/mysql.rb` in the VladTheEnterprising gem 0.2 for Ruby allows local users to obtain sensitive information by reading the MySQL root password from a temporary file before it is removed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-4995
- https://exchange.xforce.ibmcloud.com/vulnerabilities/94745
- https://web.archive.org/web/20200229054941/http://www.securityfocus.com/bid/68729
- http://www.openwall.com/lists/oss-security/2014/07/07/14
- http://www.openwall.com/lists/oss-security/2014/07/17/5
- http://www.vapid.dhs.org/advisories/VladTheEnterprising-0.2.html
