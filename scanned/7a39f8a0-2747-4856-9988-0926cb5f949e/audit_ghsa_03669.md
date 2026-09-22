# [H] Code injection in RubyGems

## Summary
Severity: High
Advisory: GHSA-76wm-422q-92mq
CVE: CVE-2019-8324
CWE: CWE-94
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-06-20
Source: https://github.com/advisories/GHSA-76wm-422q-92mq
Type: github-advisory

## Affected
- RubyGems: `rubygems-update` — affected >=2.6.0 <2.7.9
- RubyGems: `rubygems-update` — affected >=3.0.0 <3.0.2

## Details
An issue was discovered in RubyGems 2.6 and later through 3.0.2. A crafted gem with a multi-line name is not handled correctly. Therefore, an attacker could inject arbitrary code to the stub line of gemspec, which is eval-ed by code in ensure_loadable_spec during the preinstall check.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-8324
- https://access.redhat.com/errata/RHSA-2019:1972
- https://blog.rubygems.org/2019/03/05/security-advisories-2019-03.html
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rubygems-update/CVE-2019-8324.yml
- https://lists.debian.org/debian-lts-announce/2020/08/msg00027.html
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00036.html
