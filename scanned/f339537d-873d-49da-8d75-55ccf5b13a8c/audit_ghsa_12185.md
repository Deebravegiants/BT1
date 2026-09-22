# [C] Recurly gem Server-Side Request Forgery in Resource#find method

## Summary
Severity: Critical
Advisory: GHSA-x27v-x225-gq8g
CVE: CVE-2017-0905
CWE: CWE-918
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2017-12-06
Source: https://github.com/advisories/GHSA-x27v-x225-gq8g
Type: github-advisory

## Affected
- RubyGems: `recurly` — affected >=2.3.0 <2.3.10
- RubyGems: `recurly` — affected >=2.2.0 <2.2.5
- RubyGems: `recurly` — affected >=2.1.0 <2.1.11
- RubyGems: `recurly` — affected >=2.0.0 <2.0.13
- RubyGems: `recurly` — affected >=2.9.0 <2.9.2
- RubyGems: `recurly` — affected >=2.8.0 <2.8.2
- RubyGems: `recurly` — affected >=2.7.0 <2.7.8
- RubyGems: `recurly` — affected >=2.6.0 <2.6.3
- RubyGems: `recurly` — affected >=2.5.0 <2.5.4
- RubyGems: `recurly` — affected >=2.4.0 <2.4.11
- RubyGems: `recurly` — affected >=2.11.0 <2.11.3
- RubyGems: `recurly` — affected >=2.10.0 <2.10.4

## Details
The Recurly Client Ruby Library before 2.0.13, 2.1.11, 2.2.5, 2.3.10, 2.4.11, 2.5.4, 2.6.3, 2.7.8, 2.8.2, 2.9.2, 2.10.4, 2.11.3 is vulnerable to a Server-Side Request Forgery vulnerability in the `Resource#find` method that could result in compromise of API keys or other critical resources.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-0905
- https://github.com/recurly/recurly-client-ruby/commit/1bb0284d6e668b8b3d31167790ed6db1f6ccc4be
- https://hackerone.com/reports/288635
- https://github.com/recurly/recurly-client-ruby
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/recurly/CVE-2017-0905.yml
