# [M] Cocaine Gem OS Command Injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-c43v-hrmg-56r4
CVE: CVE-2013-4457
CWE: CWE-78
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-c43v-hrmg-56r4
Type: github-advisory

## Affected
- RubyGems: `cocaine` — affected >=0.4.0 <0.5.3

## Details
The Cocaine gem 0.4.0 through 0.5.2 for Ruby allows context-dependent attackers to execute arbitrary commands via a crafted has object, related to recursive variable interpolation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4457
- https://github.com/thoughtbot/cocaine
- https://github.com/thoughtbot/cocaine/blob/master/NEWS.md
- http://www.openwall.com/lists/oss-security/2013/10/22/10
