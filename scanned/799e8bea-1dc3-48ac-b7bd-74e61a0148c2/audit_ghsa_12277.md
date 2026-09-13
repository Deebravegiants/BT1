# [M] insecure temporary directory usage in passenger

## Summary
Severity: Medium
Advisory: GHSA-w6rc-q387-vpgq
CVE: CVE-2013-4136
CWE: CWE-59
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-w6rc-q387-vpgq
Type: github-advisory

## Affected
- RubyGems: `passenger` — affected >=0 <4.0.6

## Details
ext/common/ServerInstanceDir.h in Phusion Passenger gem before 4.0.6 for Ruby allows local users to gain privileges or possibly change the ownership of arbitrary directories via a symlink attack on a directory with a predictable name in /tmp/.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4136
- https://github.com/phusion/passenger/commit/5483b3292cc2af1c83033eaaadec20dba4dcfd9b
- https://code.google.com/p/phusion-passenger/issues/detail?id=910
- https://github.com/advisories/GHSA-w6rc-q387-vpgq
- https://github.com/phusion/passenger
- https://github.com/phusion/passenger/blob/release-4.0.6/NEWS
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/passenger/CVE-2013-4136.yml
- http://rhn.redhat.com/errata/RHSA-2013-1136.html
- http://www.openwall.com/lists/oss-security/2013/07/16/6
