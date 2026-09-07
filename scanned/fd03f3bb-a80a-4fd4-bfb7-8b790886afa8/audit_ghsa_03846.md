# [H] Improper Authentication in Auth0.AuthenticationApi

## Summary
Severity: High
Advisory: GHSA-c9cg-q8r2-xvjq
CVE: CVE-2019-16929
CWE: CWE-287
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2019-10-24
Source: https://github.com/advisories/GHSA-c9cg-q8r2-xvjq
Type: github-advisory

## Affected
- NuGet: `Auth0.AuthenticationApi` — affected >=5.8.0 <6.5.4

## Details
Auth0 auth0.net before 6.5.4 has Incorrect Access Control because IdentityTokenValidator can be accidentally used to validate untrusted ID tokens.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16929
- https://auth0.com/docs/security/bulletins/cve-2019-16929
