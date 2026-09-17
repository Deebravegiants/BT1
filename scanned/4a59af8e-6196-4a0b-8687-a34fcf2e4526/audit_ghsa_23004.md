# [C] Phusion Passenger SpawningKit Contains Arbitrary Read/Write Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-7cv3-gvmc-8mq5
CVE: CVE-2018-12026
CWE: CWE-59
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-7cv3-gvmc-8mq5
Type: github-advisory

## Affected
- RubyGems: `passenger` — affected >=5.3.0 <5.3.2

## Details
During the spawning of a malicious Passenger-managed application, SpawningKit in Phusion Passenger 5.3.x before 5.3.2 allows such applications to replace key files or directories in the spawning communication directory with symlinks. This then could result in arbitrary reads and writes, which in turn can result in information disclosure and privilege escalation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-12026
- https://github.com/phusion/passenger/commit/fd3717a3cd357aa0e80e1e81d4dc94a1eaf928f1
- https://blog.phusion.nl/2018/06/12/passenger-5-3-2-various-security-fixes
- https://blog.phusion.nl/passenger-5-3-2
- https://github.com/phusion/passenger
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/passenger/CVE-2018-12026.yml
- https://security.gentoo.org/glsa/201807-02
