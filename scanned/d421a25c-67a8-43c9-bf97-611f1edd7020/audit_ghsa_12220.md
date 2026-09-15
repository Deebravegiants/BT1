# [M] Rack rubygems receiving excessively long lines triggers out-of-memory error

## Summary
Severity: Medium
Advisory: GHSA-3pxh-h8hw-mj8w
CVE: CVE-2013-0183
CWE: CWE-119, CWE-400
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-3pxh-h8hw-mj8w
Type: github-advisory

## Affected
- RubyGems: `rack` — affected >=1.3.0 <1.3.8
- RubyGems: `rack` — affected >=1.4.0 <1.4.3

## Details
multipart/parser.rb in Rack 1.3.x before 1.3.8 and 1.4.x before 1.4.3 allows remote attackers to cause a denial of service (memory consumption and out-of-memory error) via a long string in a Multipart HTTP packet.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-0183
- https://github.com/rack/rack/commit/548b9af2dc0059f4c0c19728624448d84de450ff
- https://github.com/rack/rack/commit/f95113402b7239f225282806673e1b6424522b18
- https://access.redhat.com/errata/RHSA-2013:0544
- https://access.redhat.com/security/cve/CVE-2013-0183
- https://bugzilla.redhat.com/show_bug.cgi?id=895282
- https://github.com/rack/rack
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rack/CVE-2013-0183.yml
- https://groups.google.com/forum/#!topic/rack-devel/-MWPHDeGWtI
- https://groups.google.com/forum/#!topic/rack-devel/7ZKPNAjgRSs
- https://groups.google.com/forum/#%21topic/rack-devel/-MWPHDeGWtI
- https://groups.google.com/forum/#%21topic/rack-devel/7ZKPNAjgRSs
- http://lists.opensuse.org/opensuse-updates/2013-03/msg00048.html
- http://rack.github.com
- http://rhn.redhat.com/errata/RHSA-2013-0544.html
- http://rhn.redhat.com/errata/RHSA-2013-0548.html
- http://www.debian.org/security/2013/dsa-2783
