# [M] Active Record Improper Input Validation

## Summary
Severity: Medium
Advisory: GHSA-3crr-9vmg-864v
CVE: CVE-2013-1854
CWE: CWE-20
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-3crr-9vmg-864v
Type: github-advisory

## Affected
- RubyGems: `activerecord` — affected >=2.3.0 <2.3.18
- RubyGems: `activerecord` — affected >=3.1.0 <3.1.12
- RubyGems: `activerecord` — affected >=3.2.0 <3.2.13

## Details
The Active Record component in Ruby on Rails 2.3.x before 2.3.18, 3.1.x before 3.1.12, and 3.2.x before 3.2.13 processes certain queries by converting hash keys to symbols, which allows remote attackers to cause a denial of service via crafted input to a where method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-1854
- https://access.redhat.com/errata/RHSA-2013:0699
- https://access.redhat.com/errata/RHSA-2014:1863
- https://access.redhat.com/security/cve/CVE-2013-1854
- https://bugzilla.redhat.com/show_bug.cgi?id=921329
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/activerecord/CVE-2013-1854.yml
- https://groups.google.com/group/ruby-security-ann/msg/34e0d780b04308de?dmode=source&output=gplain
- http://lists.apple.com/archives/security-announce/2013/Jun/msg00000.html
- http://lists.apple.com/archives/security-announce/2013/Oct/msg00006.html
- http://lists.opensuse.org/opensuse-updates/2013-04/msg00070.html
- http://lists.opensuse.org/opensuse-updates/2013-04/msg00071.html
- http://lists.opensuse.org/opensuse-updates/2013-04/msg00075.html
- http://lists.opensuse.org/opensuse-updates/2013-04/msg00078.html
- http://lists.opensuse.org/opensuse-updates/2013-04/msg00079.html
- http://rhn.redhat.com/errata/RHSA-2013-0699.html
- http://rhn.redhat.com/errata/RHSA-2014-1863.html
- http://support.apple.com/kb/HT5784
- http://weblog.rubyonrails.org/2013/3/18/SEC-ANN-Rails-3-2-13-3-1-12-and-2-3-18-have-been-released
