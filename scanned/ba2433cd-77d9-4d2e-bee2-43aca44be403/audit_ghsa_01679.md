# [M] Ability to forge per-form CSRF tokens in Rails

## Summary
Severity: Medium
Advisory: GHSA-jp5v-5gx4-jmj9
CVE: CVE-2020-8166
CWE: CWE-352
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2020-05-26
Source: https://github.com/advisories/GHSA-jp5v-5gx4-jmj9
Type: github-advisory

## Affected
- RubyGems: `actionpack` — affected >=5.0.0 <5.2.4.3
- RubyGems: `actionpack` — affected >=6.0.0 <6.0.3.1

## Details
It is possible to, given a global CSRF token such as the one present in the authenticity_token meta tag, forge a per-form CSRF token for any action for that session.

Impact
------

Given the ability to extract the global CSRF token, an attacker would be able to construct a per-form CSRF token for that session.

Workarounds
-----------

This is a low-severity security issue. As such, no workaround is necessarily until such time as the application can be upgraded.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8166
- https://hackerone.com/reports/732415
- https://github.com/rails/rails
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/actionpack/CVE-2020-8166.yml
- https://groups.google.com/forum/#!topic/rubyonrails-security/NOjKiGeXUgw
- https://groups.google.com/g/rubyonrails-security/c/NOjKiGeXUgw
- https://www.debian.org/security/2020/dsa-4766
