# [M] JRuby denial of service via Hash Collision

## Summary
Severity: Medium
Advisory: GHSA-fmmq-j7pq-f85c
CVE: CVE-2012-5370
CWE: CWE-400
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-fmmq-j7pq-f85c
Type: github-advisory

## Affected
- Maven: `org.jruby:jruby-parent` — affected >=0 <1.7.1

## Details
JRuby computes hash values without properly restricting the ability to trigger hash collisions predictably, which allows context-dependent attackers to cause a denial of service (CPU consumption) via crafted input to an application that maintains a hash table, as demonstrated by a universal multicollision attack against the MurmurHash2 algorithm, a different vulnerability than CVE-2011-4838.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-5370
- https://github.com/jruby/jruby/commit/5e4aab28b26fd127112b76fabfac9a33b64caf77
- https://bugzilla.redhat.com/show_bug.cgi?id=880671
- http://jruby.org/2012/12/03/jruby-1-7-1
- http://rhn.redhat.com/errata/RHSA-2013-0533.html
