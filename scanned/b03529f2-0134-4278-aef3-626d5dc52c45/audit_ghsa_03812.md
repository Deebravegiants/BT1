# [C] paranoid2 gem Code backdoor

## Summary
Severity: Critical
Advisory: GHSA-4g4c-8gqh-m4vm
CVE: CVE-2019-13589
CWE: CWE-829
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-07-16
Source: https://github.com/advisories/GHSA-4g4c-8gqh-m4vm
Type: github-advisory

## Affected
- RubyGems: `paranoid2` — affected 1.1.6

## Details
The paranoid2 gem 1.1.6 for Ruby, as distributed on RubyGems.org, included a code-execution backdoor inserted by a third party. The current version, without this backdoor, is 1.1.5.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-13589
- https://github.com/rubygems/rubygems.org/issues/2051
- https://github.com/anjlab/paranoid2
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/paranoid2/CVE-2019-13589.yml
- https://rubygems.org/gems/paranoid2/versions
- https://snyk.io/vuln/SNYK-RUBY-PARANOID2-451600
- http://www.securityfocus.com/bid/109281
