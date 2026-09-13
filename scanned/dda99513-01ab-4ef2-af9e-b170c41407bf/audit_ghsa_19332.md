# [M] @cloudflare/workers-oauth-provider PKCE bypass via downgrade attack

## Summary
Severity: Medium
Advisory: GHSA-qgp8-v765-qxx9
CVE: CVE-2025-4144
CWE: CWE-287
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-05-01
Source: https://github.com/advisories/GHSA-qgp8-v765-qxx9
Type: github-advisory

## Affected
- npm: `@cloudflare/workers-oauth-provider` — affected >=0 <0.0.5

## Details
### Summary
PKCE was implemented in the OAuth implementation in workers-oauth-provider that is part of[ MCP framework](https://github.com/cloudflare/workers-mcp). However, it was found that an attacker could cause the check to be skipped.

### Impact
PKCE is a defense-in-depth mechanism against certain kinds of attacks and was an optional extension in OAuth 2.0 which became required in the OAuth 2.1 draft. (Note that the MCP specification requires OAuth 2.1.)
This bug completely bypasses PKCE protection.


### Patches
Fixed in: https://github.com/cloudflare/workers-oauth-provider/pull/27

We patched up the vulnerabilities in the latest version, v 0.0.5 of the Workers OAuth provider (https://www.npmjs.com/package/@cloudflare/workers-oauth-provider). You'll need to update your MCP servers to use that version to resolve the vulnerability.

### Workarounds
None

## References
- https://github.com/cloudflare/workers-oauth-provider/security/advisories/GHSA-qgp8-v765-qxx9
- https://nvd.nist.gov/vuln/detail/CVE-2025-4144
- https://github.com/cloudflare/workers-oauth-provider/pull/27
- https://github.com/cloudflare/workers-oauth-provider
