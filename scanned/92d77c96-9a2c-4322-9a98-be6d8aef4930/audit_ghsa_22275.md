# [H] Incorrect Access Control in Phusion Passenger

## Summary
Severity: High
Advisory: GHSA-jjhj-8gx7-x836
CVE: CVE-2018-12028
CWE: CWE-732
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-jjhj-8gx7-x836
Type: github-advisory

## Affected
- RubyGems: `passenger` — affected >=5.3.0 <5.3.2

## Details
An Incorrect Access Control vulnerability in SpawningKit in Phusion Passenger 5.3.x before 5.3.2 allows a Passenger-managed malicious application, upon spawning a child process, to report an arbitrary different PID back to Passenger's process manager. If the malicious application then generates an error, it would cause Passenger's process manager to kill said reported arbitrary PID.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-12028
- https://github.com/phusion/passenger/commit/1e7c82deb4901c438f583737d8c9f2aac264737c
- https://blog.phusion.nl/passenger-5-3-2
- https://github.com/phusion/passenger
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/passenger/CVE-2018-12028.yml
- https://security.gentoo.org/glsa/201807-02
