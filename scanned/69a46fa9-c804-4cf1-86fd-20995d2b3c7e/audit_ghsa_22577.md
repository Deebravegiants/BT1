# [M] Business Logic Errors in Para

## Summary
Severity: Medium
Advisory: GHSA-4793-8wwh-jxxr
CVE: CVE-2022-1848
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-25
Source: https://github.com/advisories/GHSA-4793-8wwh-jxxr
Type: github-advisory

## Affected
- Maven: `com.erudika:para-core` — affected >=0 <1.46.0

## Details
Paraara prior to version 1.46.0 is vulnerable to business logic errors. A user can create more than one app, even after they reach the app limit.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-1848
- https://github.com/erudika/para/commit/fa677c629842df60099daa9c23bd802bc41b48d1
- https://github.com/erudika/para
- https://huntr.dev/bounties/8dfe0877-e44b-4a1a-8eee-5c03c93ae90a
