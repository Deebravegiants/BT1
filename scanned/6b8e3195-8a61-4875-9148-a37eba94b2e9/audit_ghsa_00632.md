# [H] Cap-Strap gem for Ruby places credentials on the useradd command line

## Summary
Severity: High
Advisory: GHSA-pcm6-g2qp-9gw8
CVE: CVE-2014-4992
CWE: CWE-200
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-03-16
Source: https://github.com/advisories/GHSA-pcm6-g2qp-9gw8
Type: github-advisory

## Affected
- RubyGems: `cap-strap` — affected 0.1.5

## Details
lib/cap-strap/helpers.rb in the cap-strap gem 0.1.5 for Ruby places credentials on the useradd command line, which allows local users to obtain sensitive information by listing the process.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-4992
- https://github.com/advisories/GHSA-pcm6-g2qp-9gw8
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/cap-strap/CVE-2014-4992.yml
- https://github.com/substantial/cap-strap
- http://www.openwall.com/lists/oss-security/2014/07/07/9
- http://www.openwall.com/lists/oss-security/2014/07/17/5
- http://www.vapid.dhs.org/advisories/cap-strap-0.1.5.html
