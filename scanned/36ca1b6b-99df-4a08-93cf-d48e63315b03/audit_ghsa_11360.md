# [C] Feathers has an OAuth Callback Account Takeover issue

## Summary
Severity: Critical
Advisory: GHSA-wg9x-qfgw-pxhj
CVE: CVE-2026-29792
CWE: CWE-287
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-10
Source: https://github.com/advisories/GHSA-wg9x-qfgw-pxhj
Type: github-advisory

## Affected
- npm: `@feathersjs/authentication-oauth` — affected >=5.0.0 <5.0.42

## Details
An unauthenticated attacker can send a crafted GET request directly to `/oauth/:provider/callback` with a forged profile in the query string. The OAuth service's authentication payload has a fallback chain that reaches params.query (the raw request query) when Grant's session/state responses are empty. Since the attacker never initiated an OAuth authorize flow, Grant has no session to work with and produces no response, so the fallback fires. The forged profile then drives entity lookup and JWT minting. The attacker gets a valid access token for an existing user without ever contacting the OAuth provider. Critical (CVSS 9.8)

## References
- https://github.com/feathersjs/feathers/security/advisories/GHSA-wg9x-qfgw-pxhj
- https://nvd.nist.gov/vuln/detail/CVE-2026-29792
- https://github.com/feathersjs/feathers
