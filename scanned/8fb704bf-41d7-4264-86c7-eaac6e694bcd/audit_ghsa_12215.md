# [M] Phusion Passenger Denial of Service

## Summary
Severity: Medium
Advisory: GHSA-9qj7-jvg4-qr2x
CVE: CVE-2013-2119
CWE: CWE-377
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-9qj7-jvg4-qr2x
Type: github-advisory

## Affected
- RubyGems: `passenger` — affected >=0 <3.0.21
- RubyGems: `passenger` — affected >=4.0.1 <4.0.5

## Details
Phusion Passenger gem before 3.0.21 and 4.0.x before 4.0.5 for Ruby allows local users to cause a denial of service (prevent application start) or gain privileges by pre-creating a temporary "config" file in a directory with a predictable name in `/tmp/` before it is used by the gem.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-2119
- https://access.redhat.com/errata/RHSA-2013:1136
- https://access.redhat.com/security/cve/CVE-2013-2119
- https://bugzilla.redhat.com/show_bug.cgi?id=892813
- https://github.com/advisories/GHSA-9qj7-jvg4-qr2x
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/passenger/CVE-2013-2119.yml
- http://blog.phusion.nl/2013/05/29/phusion-passenger-3-0-21-released
- http://blog.phusion.nl/2013/05/29/phusion-passenger-4-0-5-released
- http://rhn.redhat.com/errata/RHSA-2013-1136.html
