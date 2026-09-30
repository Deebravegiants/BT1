# [H] oauth2-server through 3.1.1 vulnerable to Open Redirect

## Summary
Severity: High
Advisory: GHSA-4rg6-fm25-gc34
CVE: CVE-2020-26938
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-08-30
Source: https://github.com/advisories/GHSA-4rg6-fm25-gc34
Type: github-advisory

## Affected
- npm: `oauth2-server` — affected >=0

## Details
In oauth2-server (aka node-oauth2-server) through 3.1.1, the value of the `redirect_uri` parameter received during the authorization and token request is checked against an incorrect URI pattern (`[a-zA-Z][a-zA-Z0-9+.-]+:`) before making a redirection. This allows a malicious client to pass an XSS payload through the redirect_uri parameter while making an authorization request. NOTE: this vulnerability is similar to CVE-2020-7741.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-26938
- https://github.com/oauthjs/node-oauth2-server/issues/637
- https://github.com/oauthjs/node-oauth2-server
- https://github.com/oauthjs/node-oauth2-server/blob/91d2cbe70a0eddc53d72def96864e2de0fd41703/lib/grant-types/authorization-code-grant-type.js#L143
- https://github.com/oauthjs/node-oauth2-server/blob/91d2cbe70a0eddc53d72def96864e2de0fd41703/lib/validator/is.js#L12
- https://tools.ietf.org/html/rfc3986#section-3
- https://tools.ietf.org/html/rfc6749#section-3.1.2
