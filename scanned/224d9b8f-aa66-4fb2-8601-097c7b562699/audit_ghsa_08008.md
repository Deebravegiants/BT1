# [H] Feathers has an origin validation bypass via prefix matching

## Summary
Severity: High
Advisory: GHSA-mp4x-c34x-wv3x
CVE: CVE-2026-27192
CWE: CWE-346
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-19
Source: https://github.com/advisories/GHSA-mp4x-c34x-wv3x
Type: github-advisory

## Affected
- npm: `@feathersjs/authentication-oauth` — affected >=0 <5.0.40

## Details
The origin validation uses `startsWith()` for comparison, allowing attackers to bypass the check by registering a domain that shares a common prefix with an allowed origin.

The `getAllowedOrigin()` function checks if the Referer header starts with any allowed origin:
```javascript
// https://github.com/feathersjs/feathers/blob/dove/packages/authentication-oauth/src/strategy.ts#L75
const allowedOrigin = origins.find((current) => referer.toLowerCase().startsWith(current.toLowerCase()));
```

This comparison is insufficient as it only validates the prefix. This is exploitable when the `origins` array is configured and an attacker registers a domain starting with an allowed origin string (e.g., `https://target.com.attacker.com` bypasses `https://target.com`).

On its own, tokens are still redirected to a configured origin. However, in specific scenarios an attacker can initiate the OAuth flow from an unauthorized origin and exfiltrate tokens, achieving full account takeover.

**Credits**:  Abdelwahed Madani Yousfi (@vvxhid) / Edoardo Geraci (@b0-n0-b0) / Thomas Rinsma (@ThomasRinsma) From Codean Labs.

## References
- https://github.com/feathersjs/feathers/security/advisories/GHSA-mp4x-c34x-wv3x
- https://nvd.nist.gov/vuln/detail/CVE-2026-27192
- https://github.com/feathersjs/feathers/commit/ee19a0ae9bc2ebf23b1fe598a1f7361981b65401
- https://github.com/feathersjs/feathers
- https://github.com/feathersjs/feathers/releases/tag/v5.0.40
