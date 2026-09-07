# [M] Auth0 angular-jwt misinterprets allowlist as regex

## Summary
Severity: Medium
Advisory: GHSA-vm2p-f5j4-mj6g
CVE: CVE-2018-11537
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-vm2p-f5j4-mj6g
Type: github-advisory

## Affected
- npm: `angular-jwt` — affected >=0 <0.1.10

## Details
Auth0 angular-jwt before 0.1.10 treats whiteListedDomains entries as regular expressions, which allows remote attackers with knowledge of the `jwtInterceptorProvider.whiteListedDomains` setting to bypass the domain allowlist filter via a crafted domain.

 For example, if the setting is initialized with:

`jwtInterceptorProvider.whiteListedDomains = ['whitelisted.Example.com'];`

An attacker can set up a domain `whitelistedXexample.com` that will pass the allow list filter, as it considers the `.` separator to be a regex whildcard which matches any character.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-11537
- https://github.com/auth0/angular-jwt/pull/174
- https://github.com/auth0/angular-jwt/commit/a4f03b49c3fb47cc6375c2a33b5ac11ca3c606f0
- https://github.com/auth0/angular-jwt/commit/e368cf124443507f1710f60ae855c4c54eebc6ea
- https://auth0.com/docs/security/bulletins/cve-2018-11537
- https://github.com/auth0/angular-jwt
