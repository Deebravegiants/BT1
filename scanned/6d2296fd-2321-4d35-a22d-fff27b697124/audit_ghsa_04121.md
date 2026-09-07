# [M] Doorkeeper-openid_connect contains Open Redirect

## Summary
Severity: Medium
Advisory: GHSA-vv4c-g6q7-p3q7
CVE: CVE-2019-9837
CWE: CWE-601
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-03-25
Source: https://github.com/advisories/GHSA-vv4c-g6q7-p3q7
Type: github-advisory

## Affected
- RubyGems: `doorkeeper-openid_connect` — affected >=1.4.0 <1.5.4

## Details
Doorkeeper::OpenidConnect (aka the OpenID Connect extension for Doorkeeper) 1.4.x and 1.5.x before 1.5.4 has an open redirect via the redirect_uri field in an OAuth authorization request (that results in an error response) with the 'openid' scope and a prompt=none value. This allows phishing attacks against the authorization flow.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-9837
- https://github.com/doorkeeper-gem/doorkeeper-openid_connect/issues/61
- https://github.com/doorkeeper-gem/doorkeeper-openid_connect/pull/66
- https://github.com/doorkeeper-gem/doorkeeper-openid_connect
- https://github.com/doorkeeper-gem/doorkeeper-openid_connect/blob/master/CHANGELOG.md
