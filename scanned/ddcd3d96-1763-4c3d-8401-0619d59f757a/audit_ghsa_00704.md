# [C] SQL Injection in Geocoder

## Summary
Severity: Critical
Advisory: GHSA-864j-6qpp-cmrr
CVE: CVE-2020-7981
CWE: CWE-89
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-06-10
Source: https://github.com/advisories/GHSA-864j-6qpp-cmrr
Type: github-advisory

## Affected
- RubyGems: `geocoder` — affected >=0 <1.6.1

## Details
sql.rb in Geocoder before 1.6.1 allows Boolean-based SQL injection when `within_bounding_box` is used in conjunction with untrusted `sw_lat`, `sw_lng`, `ne_lat`, or `ne_lng` data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7981
- https://github.com/alexreisner/geocoder/commit/dcdc3d8675411edce3965941a2ca7c441ca48613
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-7981
- https://github.com/alexreisner/geocoder
- https://github.com/alexreisner/geocoder/blob/master/CHANGELOG.md#161-2020-jan-23
- https://github.com/alexreisner/geocoder/compare/v1.6.0...v1.6.1
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/geocoder/CVE-2020-7981.yml
