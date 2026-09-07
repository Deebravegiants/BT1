# [M] Rack Gem Subject to Denial of Service via Hash Collisions

## Summary
Severity: Medium
Advisory: GHSA-v6j3-7jrw-hq2p
CVE: CVE-2011-5036
CWE: CWE-328, CWE-400
Ecosystem: Maven, RubyGems
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-v6j3-7jrw-hq2p
Type: github-advisory

## Affected
- RubyGems: `rack` — affected >=0 <1.1.3
- RubyGems: `rack` — affected >=1.2.0 <1.2.5
- RubyGems: `rack` — affected >=1.3.0 <1.3.6
- Maven: `org.jruby:jruby-parent` — affected >=0 <1.6.5.1

## Details
Rack before 1.1.3, 1.2.x before 1.2.5, and 1.3.x before 1.3.6 computes hash values for form parameters without restricting the ability to trigger hash collisions predictably, which allows remote attackers to cause a denial of service (CPU consumption) by sending many crafted parameters.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-5036
- https://gist.github.com/52bbc6b9cc19ce330829
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rack/CVE-2011-5036.yml
- https://web.archive.org/web/20120201040317/http://jruby.org/2011/12/27/jruby-1-6-5-1
- https://web.archive.org/web/20130213132312/http://archives.neohapsis.com/archives/bugtraq/2011-12/0181.html
- http://www.debian.org/security/2013/dsa-2783
- http://www.kb.cert.org/vuls/id/903934
- http://www.nruns.com/_downloads/advisory28122011.pdf
- http://www.ocert.org/advisories/ocert-2011-003.html
