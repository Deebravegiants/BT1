# [H] FUXA has an unauthenticated arbitrary tag value disclosure via /api/getTagValue

## Summary
Severity: High
Advisory: GHSA-fwcm-rqvw-j3p7
CVE: CVE-2026-43946
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-fwcm-rqvw-j3p7
Type: github-advisory

## Affected
- npm: `fuxa-server` — affected >=1.3.0 <1.3.1

## Details
### Summary
 An authorization bypass in the /api/getTagValue endpoint allows unauthenticated access to tag values when the referenced script does not exist.

  ### Details
  The issue is caused by the combination of these code paths:

  - `server/api/apikeys/verify-api-or-token.js:45` sends requests without `x-api-key` to `authJwt.verifyToken(req, res, next)`.
  - `server/api/jwt-helper.js:46-64` creates a signed guest token when no `x-access-token` is provided:
    `if (!token) { token = getGuestToken(); }`
    and then populates `req.userId` / `req.userGroups` from that guest token.
  - `server/api/command/index.js:76-105` exposes `/api/getTagValue`.
  - `server/runtime/scripts/index.js:106-111` returns `true` when the referenced script does not exist:
    `if (!script) { return true; }`

  As a result, an unauthenticated request reaches `/api/getTagValue` as `guest`, and the authorization check is bypassed because `isAuthorisedByScriptName()` returns `true` when `sourceScriptName` is omitted or does not match a real script. The endpoint then returns arbitrary tag values by ID.

  ### PoC

Requests to /api/getTagValue without authentication could succeed when the authorization logic evaluated a non-existent sourceScriptName as authorized.

## References
- https://github.com/frangoteam/FUXA/security/advisories/GHSA-fwcm-rqvw-j3p7
- https://github.com/frangoteam/FUXA/pull/2260
- https://github.com/frangoteam/FUXA/commit/78534da61a91613712b44bb63c8d7da8c5df5ca4
- https://github.com/frangoteam/FUXA
- https://github.com/frangoteam/FUXA/releases/tag/v1.3.1
