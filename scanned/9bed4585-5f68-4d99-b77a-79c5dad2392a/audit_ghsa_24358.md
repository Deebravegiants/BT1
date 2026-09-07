# [H] Echor Ruby Gem credentials can be stolen via process table monitoring

## Summary
Severity: High
Advisory: GHSA-j4gx-p3x5-m987
CVE: CVE-2014-1835
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-j4gx-p3x5-m987
Type: github-advisory

## Affected
- RubyGems: `echor` — affected >=0

## Details
The perform_request function in /lib/echor/backplane.rb in echor 0.1.6 Ruby Gem allows local users to steal the login credentials by watching the process table.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-1835
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/echor/CVE-2014-1835.yml
- http://www.openwall.com/lists/oss-security/2014/01/31/10
