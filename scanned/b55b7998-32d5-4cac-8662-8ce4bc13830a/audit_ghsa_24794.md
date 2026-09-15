# [H] Insecure Permissions in Phusion Passenger

## Summary
Severity: High
Advisory: GHSA-whfx-877c-5p28
CVE: CVE-2018-12027
CWE: CWE-200
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-whfx-877c-5p28
Type: github-advisory

## Affected
- RubyGems: `passenger` — affected >=5.3.0 <5.3.2

## Details
An Insecure Permissions vulnerability in SpawningKit in Phusion Passenger 5.3.x before 5.3.2 causes information disclosure in the following situation: given a Passenger-spawned application process that reports that it listens on a certain Unix domain socket, if any of the parent directories of said socket are writable by a normal user that is not the application's user, then that non-application user can swap that directory with something else, resulting in traffic being redirected to a non-application user's process through an alternative Unix domain socket.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-12027
- https://blog.phusion.nl/passenger-5-3-2
- https://github.com/phusion/passenger
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/passenger/CVE-2018-12027.yml
- https://security.gentoo.org/glsa/201807-02
