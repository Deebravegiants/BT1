# [M] parse-server: Endpoints `/login` and `/verifyPassword` disclose MFA secrets and protected fields when `_User` get is denied

## Summary
Severity: Medium
Advisory: GHSA-75v4-m273-5j49
CVE: CVE-2026-53725
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-75v4-m273-5j49
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.8.0 <9.9.1-alpha.5

## Details
### Impact

Apps that enable MFA and deny `get` on the `_User` class via Class-Level Permissions could expose sensitive user data through the `/login` and `/verifyPassword` endpoints.

These endpoints re-fetch the user through the access-controlled query pipeline (CLP, `protectedFields`, auth-adapter sanitizers) before responding. When that re-fetch was denied by the `_User` `get` permission, the server fell back to the raw database row, exposing raw `authData` (including MFA TOTP secrets and recovery codes) and fields hidden by `protectedFields` (when `protectedFieldsOwnerExempt` is `false`).

`/verifyPassword` is the most severe: with only a username and password (no session or MFA token), an attacker who knows a victim's password could retrieve their MFA secret and recovery codes, defeating the second factor.

Only Parse Server 9.8.0 and later are affected; 8.x and earlier are not. Master and maintenance key requests are unaffected, as they bypass these controls by design.

### Patches

On a denied re-fetch, `/login` and `/verifyPassword` no longer fall back to the raw row; they return only the user's identity (plus the session token for `/login`). Master and maintenance key callers still receive the full record.

### Workarounds

None that preserve the intended `_User` `get` restriction. Upgrade to a patched version.

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-75v4-m273-5j49
- https://nvd.nist.gov/vuln/detail/CVE-2026-53725
- https://github.com/parse-community/parse-server/pull/10492
- https://github.com/parse-community/parse-server
