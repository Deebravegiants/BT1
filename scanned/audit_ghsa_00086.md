# [H] Phusion Passenger uses a known /tmp filename

## Summary
Severity: High
Advisory: GHSA-cqxw-3p7v-p9gr
CVE: CVE-2016-10345
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-08-21
Source: https://github.com/advisories/GHSA-cqxw-3p7v-p9gr
Type: github-advisory

## Affected
- RubyGems: `passenger` — affected >=0 <5.1.0

## Details
In Phusion Passenger before 5.1.0, a known /tmp filename was used during passenger-install-nginx-module execution, which could allow local attackers to gain the privileges of the passenger user

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10345
- https://github.com/phusion/passenger/commit/e5b4b0824d6b648525b4bf63d9fa37e5beeae441
- https://blog.phusion.nl/2017/01/10/passenger-5-1-1
- https://github.com/advisories/GHSA-cqxw-3p7v-p9gr
- https://github.com/phusion/passenger
- https://github.com/phusion/passenger/blob/stable-5.1/CHANGELOG
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/passenger/CVE-2016-10345.yml
