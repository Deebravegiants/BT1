# [M] xaviershay-dm-rails Gem for Ruby exposes sensitive information via the process table

## Summary
Severity: Medium
Advisory: GHSA-88p8-4vv5-82j7
CVE: CVE-2015-2179
CWE: CWE-200
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-88p8-4vv5-82j7
Type: github-advisory

## Affected
- RubyGems: `xaviershay-dm-rails` — affected >=0

## Details
xaviershay-dm-rails Gem for Ruby contains a flaw in the `execute()` function in `/datamapper/dm-rails/blob/master/lib/dm-rails/storage.rb`. The issue is due to the function exposing sensitive information via the process table. This may allow a local attack to gain access to MySQL credential information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-2179
- https://github.com/datamapper/dm-rails
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/xaviershay-dm-rails/CVE-2015-2179.yml
- http://www.vapid.dhs.org/advisory.php?v=115
