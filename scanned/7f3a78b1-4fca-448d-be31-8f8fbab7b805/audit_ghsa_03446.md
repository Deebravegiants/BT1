# [M] Cross-site scripting in actionpack

## Summary
Severity: Medium
Advisory: GHSA-35mm-cc6r-8fjp
CVE: CVE-2020-8264
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-04-07
Source: https://github.com/advisories/GHSA-35mm-cc6r-8fjp
Type: github-advisory

## Affected
- RubyGems: `actionpack` — affected >=6.0.0 <6.0.3.4

## Details
In actionpack gem >= 6.0.0, a possible XSS vulnerability exists when an application is running in development mode allowing an attacker to send or embed (in another page) a specially crafted URL which can allow the attacker to execute JavaScript in the context of the local application. This vulnerability is in the Actionable Exceptions middleware.

Workarounds
-----------
Until such time as the patch can be applied, application developers should disable the Actionable Exceptions middleware in their development environment via a line such as this one in their config/environment/development.rb: `config.middleware.delete ActionDispatch::ActionableExceptions`

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8264
- https://hackerone.com/reports/904059
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/actionpack/CVE-2020-8264.yml
- https://groups.google.com/g/rubyonrails-security/c/yQzUVfv42jk
- https://groups.google.com/g/rubyonrails-security/c/yQzUVfv42jk/m/oJWw-xhNAQAJ
