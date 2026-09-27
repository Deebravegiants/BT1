# [M] @cloudflare/workers-oauth-provider missing validation of redirect_uri on authorize endpoint

## Summary
Severity: Medium
Advisory: GHSA-4pc9-x2fx-p7vj
CVE: CVE-2025-4143
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:P/VC:H/VI:N/VA:N/SC:L/SI:N/SA:N (CVSS_V4)
Published: 2025-05-01
Source: https://github.com/advisories/GHSA-4pc9-x2fx-p7vj
Type: github-advisory

## Affected
- npm: `@cloudflare/workers-oauth-provider` — affected >=0 <0.0.5

## Details
### Summary
The OAuth implementation failed to check that redirect_uri was among the allowed set for the client_id.

### Impact
Under certain circumstances (see below), if a victim had previously authorized with a server built on workers-oath-provider, and an attacker could later trick the victim into visiting a malicious web site, then attacker could potentially steal the victim's credentials to the same OAuth server and subsequently impersonate them.

In order for the attack to be possible, the OAuth server's authorized callback must be designed to auto-approve authorizations that appear to come from an OAuth client that the victim has authorized previously. The authorization flow is not implemented by workers-oauth-provider; it is up to the application built on top to decide whether to implement such automatic re-authorization. However, many applications do implement such logic.


### Patches
Fixed in: https://github.com/cloudflare/workers-oauth-provider/pull/26

We patched up the vulnerabilities in the latest version, v 0.0.5 of the Workers OAuth provider (https://www.npmjs.com/package/@cloudflare/workers-oauth-provider). You'll need to update your MCP servers to use that version to resolve the vulnerability.


### Workarounds
None

### Note

It is a basic, well-known requirement that OAuth servers should verify that the redirect URI is among the allowed list for the client, both during the authorization flow and subsequently when exchanging the authorization code for an access token. workers-oauth-provider implemented only the latter check, not the former. Unfortunately, the former is the much more important check.

Readers who are familiar with OAuth may recognize that failing to check redirect URIs against the allowed list is a well-known, basic mistake, covered extensively in the RFC and elsewhere. The author of this library would like everyone to know that he was, in fact, well-aware of this requirement, thought about it a lot while designing the library, and then, somehow, forgot to actually make sure the check was in the code. That is, it's not that he didn't know what he was doing, it's that he knew what he was doing but flubbed it.

## References
- https://github.com/cloudflare/workers-oauth-provider/security/advisories/GHSA-4pc9-x2fx-p7vj
- https://nvd.nist.gov/vuln/detail/CVE-2025-4143
- https://github.com/cloudflare/workers-oauth-provider/pull/26
- https://github.com/cloudflare/workers-oauth-provider
