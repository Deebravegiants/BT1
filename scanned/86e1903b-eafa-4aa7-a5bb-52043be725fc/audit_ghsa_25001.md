# [H] RubyGems Link Following vulnerability

## Summary
Severity: High
Advisory: GHSA-gx69-6cp4-hxrj
CVE: CVE-2018-1000073
CWE: CWE-59
Ecosystem: Maven, RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-gx69-6cp4-hxrj
Type: github-advisory

## Affected
- RubyGems: `rubygems-update` — affected >=0 <2.7.6
- Maven: `org.jruby:jruby-stdlib` — affected >=0 <9.1.16.0

## Details
RubyGems version Ruby 2.2 series: 2.2.9 and earlier, Ruby 2.3 series: 2.3.6 and earlier, Ruby 2.4 series: 2.4.3 and earlier, Ruby 2.5 series: 2.5.0 and earlier, prior to trunk revision 62422 contains a Directory Traversal vulnerability in `install_location` function of `package.rb` that can result in path traversal when writing to a symlinked basedir outside of the root. This vulnerability appears to have been fixed in 2.7.6.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000073
- https://github.com/rubygems/rubygems/commit/1b931fc03b819b9a0214be3eaca844ef534175e2
- https://github.com/jruby/jruby/commit/0b06b48ab4432237ce5fc1bef47f2c6bcf7843f7
- https://www.debian.org/security/2018/dsa-4259
- https://www.debian.org/security/2018/dsa-4219
- https://usn.ubuntu.com/3621-1
- https://lists.debian.org/debian-lts-announce/2018/08/msg00028.html
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rubygems-update/CVE-2018-1000073.yml
- https://github.com/rubygems/rubygems
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=925986
- https://access.redhat.com/errata/RHSA-2020:0663
- https://access.redhat.com/errata/RHSA-2020:0591
- https://access.redhat.com/errata/RHSA-2020:0542
- https://access.redhat.com/errata/RHSA-2019:2028
- https://access.redhat.com/errata/RHSA-2018:3731
- https://access.redhat.com/errata/RHSA-2018:3730
- https://access.redhat.com/errata/RHSA-2018:3729
- http://blog.rubygems.org/2018/02/15/2.7.6-released.html
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00036.html
