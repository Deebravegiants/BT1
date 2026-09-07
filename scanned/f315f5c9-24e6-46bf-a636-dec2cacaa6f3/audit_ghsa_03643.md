# [H] RubyGems Escape sequence injection vulnerability in api response handling

## Summary
Severity: High
Advisory: GHSA-3h4r-pjv6-cph9
CVE: CVE-2019-8323
CWE: CWE-74
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2019-06-20
Source: https://github.com/advisories/GHSA-3h4r-pjv6-cph9
Type: github-advisory

## Affected
- RubyGems: `rubygems-update` — affected >=2.6.0 <2.7.9
- RubyGems: `rubygems-update` — affected >=3.0.0 <3.0.2

## Details
An issue was discovered in RubyGems 2.6 and later through 3.0.2. Gem::GemcutterUtilities#with_response may output the API response to stdout as it is. Therefore, if the API side modifies the response, escape sequence injection may occur.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-8323
- https://hackerone.com/reports/315081
- https://blog.rubygems.org/2019/03/05/security-advisories-2019-03.html
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rubygems-update/CVE-2019-8323.yml
- https://lists.debian.org/debian-lts-announce/2020/08/msg00027.html
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00036.html
