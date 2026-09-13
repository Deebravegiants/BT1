# [M] RubyGems Improper Input Validation vulnerability

## Summary
Severity: Medium
Advisory: GHSA-gv86-43rv-79m2
CVE: CVE-2018-1000077
CWE: CWE-20
Ecosystem: Maven, RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-gv86-43rv-79m2
Type: github-advisory

## Affected
- RubyGems: `rubygems-update` — affected >=0 <2.7.6
- Maven: `org.jruby:jruby-stdlib` — affected >=0 <9.1.16.0

## Details
RubyGems version Ruby 2.2 series: 2.2.9 and earlier, Ruby 2.3 series: 2.3.6 and earlier, Ruby 2.4 series: 2.4.3 and earlier, Ruby 2.5 series: 2.5.0 and earlier, prior to trunk revision 62422 contains a Improper Input Validation vulnerability in ruby gems specification homepage attribute that can result in a malicious gem setting an invalid homepage URL. This vulnerability is fixed in 2.7.6.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000077
- https://github.com/jruby/jruby/commit/0b06b48ab4432237ce5fc1bef47f2c6bcf7843f7
- https://github.com/rubygems/rubygems/commit/5971b486d4dbb2bad5d3445b3801c456eb0ce183
- https://github.com/rubygems/rubygems/commit/feadefc2d351dcb95d6492f5ad17ebca546eb964
- https://www.debian.org/security/2018/dsa-4259
- https://www.debian.org/security/2018/dsa-4219
- https://usn.ubuntu.com/3621-1
- https://lists.debian.org/debian-lts-announce/2019/05/msg00028.html
- https://lists.debian.org/debian-lts-announce/2018/07/msg00012.html
- https://lists.debian.org/debian-lts-announce/2018/04/msg00023.html
- https://lists.debian.org/debian-lts-announce/2018/04/msg00001.html
- https://lists.debian.org/debian-lts-announce/2018/04/msg00000.html
- https://access.redhat.com/errata/RHSA-2020:0663
- https://access.redhat.com/errata/RHSA-2020:0591
- https://access.redhat.com/errata/RHSA-2020:0542
- https://access.redhat.com/errata/RHSA-2019:2028
- https://access.redhat.com/errata/RHSA-2018:3731
- https://access.redhat.com/errata/RHSA-2018:3730
- https://access.redhat.com/errata/RHSA-2018:3729
- http://blog.rubygems.org/2018/02/15/2.7.6-released.html
