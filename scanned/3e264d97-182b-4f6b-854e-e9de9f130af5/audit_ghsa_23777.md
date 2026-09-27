# [M] RubyGems does not verify SSL certificate

## Summary
Severity: Medium
Advisory: GHSA-5mgj-mvv8-46mw
CVE: CVE-2012-2126
Ecosystem: RubyGems
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-5mgj-mvv8-46mw
Type: github-advisory

## Affected
- RubyGems: `rubygems-update` — affected >=0 <1.8.23

## Details
RubyGems before 1.8.23 does not verify an SSL certificate, which allows remote attackers to modify a gem during installation via a man-in-the-middle attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-2126
- https://github.com/rubygems/rubygems/commit/d4c7eafb8efe1e13a7abf5be5a5b4548870b15b7
- https://bugzilla.redhat.com/show_bug.cgi?id=814718
- https://github.com/rubygems/rubygems
- https://github.com/rubygems/rubygems/blob/1.8/History.txt
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rubygems-update/CVE-2012-2126.yml
- http://rhn.redhat.com/errata/RHSA-2013-1203.html
- http://rhn.redhat.com/errata/RHSA-2013-1441.html
- http://rhn.redhat.com/errata/RHSA-2013-1852.html
- http://www.openwall.com/lists/oss-security/2012/04/20/24
- http://www.ubuntu.com/usn/USN-1582-1
