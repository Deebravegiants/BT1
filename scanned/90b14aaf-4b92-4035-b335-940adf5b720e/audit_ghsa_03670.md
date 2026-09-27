# [H] RubyGems Escape sequence injection in errors

## Summary
Severity: High
Advisory: GHSA-4wm8-fjv7-j774
CVE: CVE-2019-8325
CWE: CWE-74
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2019-06-20
Source: https://github.com/advisories/GHSA-4wm8-fjv7-j774
Type: github-advisory

## Affected
- RubyGems: `rubygems-update` — affected >=2.6.0 <2.7.9
- RubyGems: `rubygems-update` — affected >=3.0.0 <3.0.2

## Details
An issue was discovered in RubyGems 2.6 and later through 3.0.2. Since Gem::CommandManager#run calls alert_error without escaping, escape sequence injection is possible. (There are many ways to cause an error.)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-8325
- https://blog.rubygems.org/2019/03/05/security-advisories-2019-03.html
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rubygems-update/CVE-2019-8325.yml
- https://lists.debian.org/debian-lts-announce/2020/08/msg00027.html
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00036.html
