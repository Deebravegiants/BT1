# [M] Rack vulnerable to REDoS

## Summary
Severity: Medium
Advisory: GHSA-h77x-m5q8-c29h
CVE: CVE-2012-6109
CWE: CWE-835
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-h77x-m5q8-c29h
Type: github-advisory

## Affected
- RubyGems: `rack` — affected >=0 <1.1.4
- RubyGems: `rack` — affected >=1.2.0 <1.2.6
- RubyGems: `rack` — affected >=1.3.0 <1.3.7
- RubyGems: `rack` — affected >=1.4.0 <1.4.2

## Details
`lib/rack/multipart.rb` in Rack before 1.1.4, 1.2.x before 1.2.6, 1.3.x before 1.3.7, and 1.4.x before 1.4.2 uses an incorrect regular expression, which allows remote attackers to cause a denial of service (infinite loop) via a crafted Content-Disposion header.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-6109
- https://github.com/rack/rack/commit/c9f65df37a151821eb88ddd1dc404b83e52c52d5
- https://access.redhat.com/errata/RHSA-2013:0544
- https://access.redhat.com/security/cve/CVE-2012-6109
- https://bugzilla.redhat.com/show_bug.cgi?id=895277
- https://github.com/rack/rack
- https://github.com/rack/rack/blob/master/README.rdoc
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rack/CVE-2012-6109.yml
- https://groups.google.com/forum/#!msg/rack-devel/1w4_fWEgTdI/XAkSNHjtdTsJ
- https://groups.google.com/forum/#%21msg/rack-devel/1w4_fWEgTdI/XAkSNHjtdTsJ
- https://rhn.redhat.com/errata/RHSA-2013-0544.html
