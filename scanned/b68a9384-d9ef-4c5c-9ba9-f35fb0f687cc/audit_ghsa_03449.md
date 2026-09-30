# [H] Code Injection in oauth2-server

## Summary
Severity: High
Advisory: GHSA-2fw4-mgq9-39cx
CVE: CVE-2017-18924
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-04-22
Source: https://github.com/advisories/GHSA-2fw4-mgq9-39cx
Type: github-advisory

## Affected
- npm: `oauth2-server` — affected >=0

## Details
"oauth2-server (aka node-oauth2-server) through 3.1.1 implements OAuth 2.0 without PKCE. It does not prevent authorization code injection. This is similar to CVE-2020-7692. NOTE: the vendor states 'As RFC7636 is an extension, I think the claim in the Readme of "RFC 6749 compliant" is valid and not misleading and I also therefore wouldn't describe this as a "vulnerability" with the library per se.'"

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18924
- https://github.com/oauthjs/node-oauth2-server/issues/637
- https://github.com/oauthjs/node-oauth2-server/pull/452
- https://codeburst.io/missing-the-point-in-securing-oauth-2-0-83968708b467
- https://tools.ietf.org/html/draft-ietf-oauth-security-topics-15
- https://tools.ietf.org/html/rfc7636
