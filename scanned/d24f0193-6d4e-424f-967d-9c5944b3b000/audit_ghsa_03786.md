# [M] Authentication Bypass in Devise

## Summary
Severity: Medium
Advisory: GHSA-fcjw-8rhj-gwwc
CVE: CVE-2019-16109
CWE: CWE-284
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2019-09-11
Source: https://github.com/advisories/GHSA-fcjw-8rhj-gwwc
Type: github-advisory

## Affected
- RubyGems: `devise` — affected >=0 <4.7.1

## Details
An issue was discovered in Plataformatec Devise before 4.7.1. It confirms accounts upon receiving a request with a blank confirmation_token, if a database record has a blank value in the confirmation_token column. (However, there is no scenario within Devise itself in which such database records would exist.)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16109
- https://github.com/plataformatec/devise/issues/5071
- https://github.com/plataformatec/devise/pull/5132
- https://github.com/plataformatec/devise
- https://github.com/plataformatec/devise/compare/v4.7.0...v4.7.1
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/devise/CVE-2019-16109.yml
