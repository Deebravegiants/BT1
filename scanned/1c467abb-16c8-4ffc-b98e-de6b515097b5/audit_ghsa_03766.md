# [C] Airbrake keys not being filtered

## Summary
Severity: Critical
Advisory: GHSA-2p82-v77v-mppr
CVE: CVE-2019-16060
CWE: CWE-200
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-09-11
Source: https://github.com/advisories/GHSA-2p82-v77v-mppr
Type: github-advisory

## Affected
- RubyGems: `airbrake-ruby` — affected >=4.2.3 <4.2.4

## Details
The Airbrake Ruby notifier 4.2.3 for Airbrake mishandles the blacklist_keys configuration option and consequently may disclose passwords to unauthorized actors. This is fixed in 4.2.4 (also, 4.2.2 and earlier are unaffected).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16060
- https://github.com/airbrake/airbrake-ruby/issues/468
- https://github.com/airbrake/airbrake-ruby/pull/469/commits/d29925e7838031bf7dea7016b22de52532503796
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/airbrake-ruby/CVE-2019-16060.yml
