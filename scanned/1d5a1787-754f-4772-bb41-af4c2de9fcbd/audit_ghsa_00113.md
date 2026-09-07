# [H] Doorkeeper subject to Incorrect Permission Assignment

## Summary
Severity: High
Advisory: GHSA-694m-jhr9-pf77
CVE: CVE-2018-1000211
CWE: CWE-732
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-08-13
Source: https://github.com/advisories/GHSA-694m-jhr9-pf77
Type: github-advisory

## Affected
- RubyGems: `doorkeeper` — affected >=4.2.0 <4.4.0

## Details
Doorkeeper version 4.2.0 and later contains a Incorrect Access Control vulnerability in Token revocation API's authorized method that can result in Access tokens are not revoked for public OAuth apps, leaking access until expiry.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000211
- https://github.com/doorkeeper-gem/doorkeeper/issues/891
- https://github.com/doorkeeper-gem/doorkeeper/pull/1119
- https://github.com/advisories/GHSA-694m-jhr9-pf77
- https://github.com/doorkeeper-gem/doorkeeper
