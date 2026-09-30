# [M] Flowise: Mass Assignment in PUT /api/v1/user Allows Authenticated Users to Override Password Hash and Bypass Password Change Verification

## Summary
Severity: Medium
Advisory: GHSA-59fh-9f3p-7m39
CWE: CWE-915
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-20
Source: https://github.com/advisories/GHSA-59fh-9f3p-7m39
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.1.2

## Details
### Summary
A Mass Assignment vulnerability in the PUT /api/v1/user endpoint allows authenticated users to directly modify restricted user fields, including the credential (password hash), bypassing the intended password change workflow.

Because the endpoint forwards the entire request body to the service layer without filtering, an attacker can override the credential field without providing the current password.

This bypasses several security protections including:

- old password verification
- password hashing enforcement
- password policy validation
- session invalidation on password change

While the vulnerability cannot be used to modify other users due to an ID check in the controller, it allows attackers who obtain a temporary session (e.g., via token theft or XSS) to establish persistent account access.

### Details
The endpoint **PUT /api/v1/user** allows authenticated users to update their user profile.

The controller checks that the authenticated user matches the provided id, preventing direct IDOR:

```typescript
const currentUser = req.user
const { id } = req.body

if (currentUser.id !== id) {
    throw new InternalFlowiseError(StatusCodes.FORBIDDEN)
}
```

However, the controller forwards the entire request body directly to the service layer without filtering:

```typescript
const user = await userService.updateUser(req.body)
```

Inside UserService.updateUser, the incoming data is merged into the existing user entity:

```typescript
updatedUser = queryRunner.manager.merge(User, oldUserData, newUserData)
```

Because newUserData is derived from req.body and there is no field allowlist, any field present in the User entity may be modified.

This includes sensitive fields such as:

- credential
- tempToken
- tokenExpiry
- status
- email

The service implements a secure password change workflow that requires the following fields:

```typescript
oldPassword
newPassword
confirmPassword

```

Example code:

```typescript
if (newUserData.oldPassword && newUserData.newPassword && newUserData.confirmPassword) {
    if (!compareHash(newUserData.oldPassword, oldUserData.credential)) {
        throw new InternalFlowiseError(StatusCodes.BAD_REQUEST)
    }

    newUserData.credential = this.encryptUserCredential(newUserData.newPassword)
}
```
However, this logic can be bypassed by directly supplying a credential value in the request body.

Because the merge operation applies all fields from newUserData, the supplied credential hash will overwrite the stored password hash.

### PoC
**Step 1 -  Authenticate**

Login as any normal user and obtain a valid JWT token.

**POST /api/v1/auth/login**

**Step 2 - Generate a password hash**

Generate a bcrypt hash for a password you control.

Example:

bcrypt("attacker_password")

Example hash:

$2b$10$abc123examplehashvalue...

Step 3 - Send crafted update request

```http
PUT /api/v1/user
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "id": "<your-user-id>",
  "credential": "$2b$10$abc123examplehashvalue..."
}
```

Step 4 - Login with attacker password

The password hash in the database is replaced by the supplied value.

The attacker can now authenticate using:

**attacker_password**

without ever providing the previous password.

### Impact
This vulnerability allows authenticated users to bypass the password change security controls.

Security protections that are bypassed include:

current password verification

password hashing enforcement

password policy validation

session invalidation on password change

Although the controller prevents modification of other users' accounts, the vulnerability enables persistence after account compromise.

Example attack scenario:

- An attacker temporarily obtains a user's session (XSS, token leak, shared device, etc.)
- The attacker sends the crafted update request with a new password hash
- The attacker now permanently controls the account
- Authentication logic bypass
- Privilege persistence after compromise
- Weak account recovery guarantees

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-59fh-9f3p-7m39
- https://github.com/FlowiseAI/Flowise
