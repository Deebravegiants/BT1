# [M] Improper Access Control in passport-oauth2

## Summary
Severity: Medium
Advisory: GHSA-f794-r6xc-hf3v
CVE: CVE-2021-41580
CWE: CWE-287
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2021-09-29
Source: https://github.com/advisories/GHSA-f794-r6xc-hf3v
Type: github-advisory

## Affected
- npm: `passport-oauth2` — affected >=0 <1.6.1

## Details
The passport-oauth2 package before 1.6.1 for Node.js mishandles the error condition of failure to obtain an access token. This is exploitable in certain use cases where an OAuth identity provider uses an HTTP 200 status code for authentication-failure error reports, and an application grants authorization upon simply receiving the access token (i.e., does not try to use the token). NOTE: the passport-oauth2 vendor does not consider this a passport-oauth2 vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-41580
- https://github.com/jaredhanson/passport-oauth2/pull/144
- https://github.com/jaredhanson/passport-oauth2/commit/8e3bcdff145a2219033bd782fc517229fe3e05ea
- https://github.com/jaredhanson/passport-oauth2
- https://github.com/jaredhanson/passport-oauth2/compare/v1.6.0...v1.6.1
- https://medium.com/passportjs/no-access-token-no-service-7fb017c9e262
