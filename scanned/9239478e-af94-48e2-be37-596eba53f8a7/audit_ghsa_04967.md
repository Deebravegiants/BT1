# [M] NocoDB: OAuth Authorization Code Race Condition

## Summary
Severity: Medium
Advisory: GHSA-8m7c-hf24-5g47
CVE: CVE-2026-47386
CWE: CWE-362
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-05
Source: https://github.com/advisories/GHSA-8m7c-hf24-5g47
Type: github-advisory

## Affected
- npm: `nocodb` — affected >=0 <2026.05.1

## Details
### Summary
Two concurrent token-exchange requests using the same OAuth authorization code could
each mint a distinct valid `(access_token, refresh_token)` pair, breaking the
single-use guarantee that PKCE relies on.

### Details
The token-exchange flow read `is_used` and called `markAsUsed` as an unconditional
update at the end of the path. A new `OAuthAuthorizationCode.claimByCode` method now
performs an atomic compare-and-swap (`WHERE code = ? AND is_used = false`) and is
called immediately before `OAuthToken.insert`, after redirect-URI, PKCE, and client
authentication have all succeeded. Only the first concurrent caller's `UPDATE` wins;
the rest see `invalid_grant: Authorization code has already been used`.

### Impact
An attacker who has observed an authorization code and the corresponding PKCE
verifier (for example through a malicious OAuth-aware client or by racing a real
exchange) could obtain a long-lived refresh token in addition to the legitimate one.

### Credit
This issue was reported by [@eddieran](https://github.com/eddieran).

## References
- https://github.com/nocodb/nocodb/security/advisories/GHSA-8m7c-hf24-5g47
- https://nvd.nist.gov/vuln/detail/CVE-2026-47386
- https://github.com/nocodb/nocodb
- https://github.com/nocodb/nocodb/releases/tag/2026.05.1
