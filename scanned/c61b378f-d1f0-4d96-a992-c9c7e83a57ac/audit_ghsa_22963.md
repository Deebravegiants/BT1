# [M] RubyGems HTTPS to HTTP redirect

## Summary
Severity: Medium
Advisory: GHSA-228f-g3h7-3fj3
CVE: CVE-2012-2125
Ecosystem: RubyGems
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-228f-g3h7-3fj3
Type: github-advisory

## Affected
- RubyGems: `rubygems-update` — affected >=0 <1.8.23

## Details
RubyGems before 1.8.23 can redirect HTTPS connections to HTTP, which makes it easier for remote attackers to observe or modify a gem during installation via a man-in-the-middle attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-2125
- https://bugzilla.redhat.com/show_bug.cgi?id=814718
- https://github.com/rubygems/rubygems
- https://github.com/rubygems/rubygems/blob/1.8/History.txt
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rubygems-update/CVE-2012-2125.yml
- http://rhn.redhat.com/errata/RHSA-2013-1203.html
- http://rhn.redhat.com/errata/RHSA-2013-1441.html
- http://rhn.redhat.com/errata/RHSA-2013-1852.html
- http://www.openwall.com/lists/oss-security/2012/04/20/24
- http://www.ubuntu.com/usn/USN-1582-1
