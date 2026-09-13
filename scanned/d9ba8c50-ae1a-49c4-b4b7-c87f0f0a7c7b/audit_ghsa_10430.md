# [H] listmonk's active sessions remain valid after password reset and password change

## Summary
Severity: High
Advisory: GHSA-h5j9-cvrw-v5qh
CVE: CVE-2026-34828
CWE: CWE-613
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-h5j9-cvrw-v5qh
Type: github-advisory

## Affected
- Go: `github.com/knadh/listmonk` — affected >=1.1.1-0.20241028090858-319053dd7a90 <1.1.1-0.20260329113754-1b5e8d38c778

## Details
### Summary
A session management vulnerability allows previously issued authenticated sessions to remain valid after sensitive account security changes, specifically password reset and password change. As a result, an attacker who has already obtained a valid session cookie can retain access to the account even after the victim changes or resets their password.

This weakens account recovery and session security guarantees. I reproduced the issue on listmonk v6.0.0.

### Details
The application updates account credentials successfully, but existing active sessions are not revoked afterward.

This behavior was confirmed in two flows:

1. **Password reset flow**
   - A user resets their password through the forgot/reset flow.
   - The old password becomes invalid.
   - The new password works.
   - However, a session cookie issued **before** the reset remains valid and continues to authenticate successfully.

2. **Authenticated password change flow**
   - The same user logs in from two separate sessions.
   - Using session A, the password is changed through the authenticated profile endpoint.
   - The old password becomes invalid.
   - The new password works.
   - However, session B, issued before the password change, remains valid and continues to authenticate successfully.

From the source review, the reset flow consumes the reset token, updates the password, and creates a fresh session, but there does not appear to be any revocation of older sessions. The same applies to the profile password change flow.

Relevant code areas observed during review:
- `cmd/auth.go` — forgot/reset flow
- `cmd/users.go` — authenticated profile update flow
- `internal/core/users.go` — password update path

Additionally:
- It was verified that reset links are single-use.
- It was verified that password reset on a TOTP-enabled account still enforces TOTP on fresh login.
- However, already-issued sessions still remain valid after reset.

### PoC
#### Case 1: Password reset does not revoke existing session

1. Create or use a normal user account.
2. Log in as that user and save the authenticated session cookie.
3. Trigger forgot-password for the account.
4. Use the emailed reset link and set a new password.
5. Verify:
   - the old password no longer works
   - the new password works
6. Replay the **old pre-reset session cookie** against an authenticated endpoint such as `/api/profile`.

Example validation request:
```http
GET /api/profile HTTP/1.1
Host: 127.0.0.1:9000
Cookie: session=<old_pre_reset_session>
```

Observed result:

Server returns `HTTP/1.1 200 OK`
Response contains the authenticated user profile

#### Case 2: Password change does not revoke other active sessions

1. Log in twice as the same user and save two authenticated session cookies:
   - session A
   - session B

2. Using session A, change the password through the authenticated profile update endpoint.

3. Verify:
   - the old password no longer works
   - the new password works

4. Replay session B against an authenticated endpoint such as `/api/profile`.

Example password change request:
```http
PUT /api/profile HTTP/1.1
Host: 127.0.0.1:9000
Cookie: session=<session_A>
Content-Type: application/json

{
  "name":"victim1",
  "email":"victim1@test.local",
  "password":"VictimChanged123"
}
```

Then validate session B:
```http
GET /api/profile HTTP/1.1
Host: 127.0.0.1:9000
Cookie: session=<session_B>
```

Observed result:
- Server returns `HTTP/1.1 200 OK`
- Response contains the authenticated user profile

## Impact

This issue allows persistence of unauthorized access after credential recovery actions.

If an attacker has already stolen a valid session cookie through any means (for example malware, browser compromise, XSS, shared machine access, proxy leakage, or other session theft), the victim cannot fully recover the account by changing or resetting the password alone. The attacker’s existing session remains valid.

This impacts account recovery expectations and session security for all authenticated users, including users with TOTP enabled.

## Attachment
[listmonk-session-report.zip](https://github.com/user-attachments/files/25975979/listmonk-session-report.zip)

## References
- https://github.com/knadh/listmonk/security/advisories/GHSA-h5j9-cvrw-v5qh
- https://nvd.nist.gov/vuln/detail/CVE-2026-34828
- https://github.com/knadh/listmonk/commit/db82035d619348949512dafdaf60c86037cafc9e
- https://github.com/knadh/listmonk
- https://github.com/knadh/listmonk/releases/tag/v6.1.0
