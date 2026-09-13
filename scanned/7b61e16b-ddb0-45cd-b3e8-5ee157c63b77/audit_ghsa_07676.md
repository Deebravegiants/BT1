# [H] Feathers has an open redirect in OAuth callback enables account takeover

## Summary
Severity: High
Advisory: GHSA-ppf9-4ffw-hh4p
CVE: CVE-2026-27191
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:A/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-19
Source: https://github.com/advisories/GHSA-ppf9-4ffw-hh4p
Type: github-advisory

## Affected
- npm: `@feathersjs/authentication-oauth` — affected >=0 <5.0.40

## Details
### Description

The `redirect` query parameter is appended to the base origin without validation, allowing attackers to steal access tokens via URL authority injection. This leads to full account takeover, as the attacker obtains the victim's access token and can impersonate them.

The application constructs the final redirect URL by concatenating the base origin with the user-supplied `redirect` parameter:
```javascript
// https://github.com/feathersjs/feathers/blob/dove/packages/authentication-oauth/src/service.ts#L158C3-L176C4
const { redirect } = query;
...
session.redirect = redirect;

// https://github.com/feathersjs/feathers/blob/dove/packages/authentication-oauth/src/strategy.ts#L98
const redirectUrl = `${redirect}${queryRedirect}`;
```

Where:
- `redirect` = base origin from config (e.g., `https://target.com`)
- `queryRedirect` = user input from `?redirect=` parameter

This is exploitable when the `origins` array is configured and origin values do not end with `/`.  An attacker can supply `@attacker.com` as the redirect value results in `https://target.com@attacker.com#access_token=...`, where the browser interprets `attacker.com` as the host, leading to full account takeover.

**Credits**:  Abdelwahed Madani Yousfi (@vvxhid) / Edoardo Geraci (@b0-n0-b0) / Thomas Rinsma (@ThomasRinsma) From Codean Labs.

## References
- https://github.com/feathersjs/feathers/security/advisories/GHSA-ppf9-4ffw-hh4p
- https://nvd.nist.gov/vuln/detail/CVE-2026-27191
- https://github.com/feathersjs/feathers/commit/ee19a0ae9bc2ebf23b1fe598a1f7361981b65401
- https://github.com/feathersjs/feathers
- https://github.com/feathersjs/feathers/releases/tag/v5.0.40
