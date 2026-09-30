# [M] Rack ReDoS Vulnerability in HTTP Accept Headers Parsing

## Summary
Severity: Medium
Advisory: GHSA-cj83-2ww7-mvq7
CVE: CVE-2024-39316
CWE: CWE-1333
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-07-03
Source: https://github.com/advisories/GHSA-cj83-2ww7-mvq7
Type: github-advisory

## Affected
- RubyGems: `rack` — affected >=3.1.0 <3.1.5

## Details
### Summary

A Regular Expression Denial of Service (ReDoS) vulnerability exists in the `Rack::Request::Helpers` module when parsing HTTP Accept headers. This vulnerability can be exploited by an attacker sending specially crafted `Accept-Encoding` or `Accept-Language` headers, causing the server to spend excessive time processing the request and leading to a Denial of Service (DoS).

### Details

The fix for https://github.com/rack/rack/security/advisories/GHSA-54rr-7fvw-6x8f was not applied to the main branch and thus while the issue was fixed for the Rack v3.0 release series, it was not fixed in the v3.1 release series until v3.1.5.

## References
- https://github.com/rack/rack/security/advisories/GHSA-54rr-7fvw-6x8f
- https://github.com/rack/rack/security/advisories/GHSA-cj83-2ww7-mvq7
- https://nvd.nist.gov/vuln/detail/CVE-2024-39316
- https://github.com/rack/rack/commit/412c980450ca729ee37f90a2661f166a9665e058
- https://advisory.dw1.io/61
- https://github.com/rack/rack
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rack/CVE-2024-39316.yml
