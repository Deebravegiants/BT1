# [M] Phusion Passenger information disclosure

## Summary
Severity: Medium
Advisory: GHSA-cv3f-px9r-54hm
CVE: CVE-2017-16355
CWE: CWE-200
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-cv3f-px9r-54hm
Type: github-advisory

## Affected
- RubyGems: `passenger` — affected >=0 <5.1.11

## Details
In agent/Core/SpawningKit/Spawner.h in Phusion Passenger 5.1.10 (fixed in Passenger Open Source 5.1.11 and Passenger Enterprise 5.1.10), if Passenger is running as root, it is possible to list the contents of arbitrary files on a system by symlinking a file named REVISION from the application root folder to a file of choice and querying passenger-status --show=xml.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16355
- https://github.com/phusion/passenger/commit/4043718264095cde6623c2cbe8c644541036d7bf
- https://blog.phusion.nl/2017/10/13/passenger-security-advisory-5-1-11
- https://github.com/phusion/passenger
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/passenger/CVE-2017-16355.yml
- https://seclists.org/bugtraq/2019/Mar/34
- https://www.debian.org/security/2019/dsa-4415
