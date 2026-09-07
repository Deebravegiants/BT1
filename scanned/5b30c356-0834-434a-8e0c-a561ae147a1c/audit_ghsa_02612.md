# [H] Clearance Gem Open Redirect Vulnerability

## Summary
Severity: High
Advisory: GHSA-4hpq-rjcx-7vj9
CVE: CVE-2021-23435
CWE: CWE-601
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2021-09-13
Source: https://github.com/advisories/GHSA-4hpq-rjcx-7vj9
Type: github-advisory

## Affected
- RubyGems: `clearance` — affected >=0 <2.5.0

## Details
This affects the package clearance before 2.5.0. The vulnerability can be possible when users are able to set the value of `session[:return_to]`. If the value used for return_to contains multiple leading slashes (`/////example.com`) the user ends up being redirected to the external domain that comes after the slashes (`http://example.com`).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23435
- https://github.com/thoughtbot/clearance/pull/945
- https://github.com/advisories/GHSA-4hpq-rjcx-7vj9
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/clearance/CVE-2021-23435.yml
- https://github.com/thoughtbot/clearance
- https://snyk.io/vuln/SNYK-RUBY-CLEARANCE-1577284
