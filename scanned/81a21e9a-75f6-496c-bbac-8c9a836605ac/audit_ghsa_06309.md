# [C] Flowise: Unauthenticated OAuth2 token refresh endpoint returns access tokens — enables token theft for any connected service

## Summary
Severity: Critical
Advisory: GHSA-qgvm-j2hm-6m38
CVE: CVE-2026-70478
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:N/SC:H/SI:L/SA:N (CVSS_V4)
Published: 2026-08-04
Source: https://github.com/advisories/GHSA-qgvm-j2hm-6m38
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.1.3

## Details
### Summary

The OAuth2 token refresh endpoint (`POST /api/v1/oauth2-credential/refresh/:credentialId`) is in `WHITELIST_URLS`, meaning it requires **no authentication**. It decrypts the stored credential (containing `clientId`, `clientSecret`, `refresh_token`), sends a refresh request to the configured OAuth provider, and returns the new `access_token` directly in the response body.

### Root Cause

```typescript
// packages/server/src/routes/oauth2/index.ts:393-402
res.json({
    success: true,
    message: 'OAuth2 token refreshed successfully',
    credentialId: credential.id,
    tokenInfo: {
        ...tokenData,  // ← includes access_token!
        has_new_refresh_token: !!tokenData.refresh_token,
        expires_at: updatedCredentialData.expires_at
    }
})
```

Whitelist entry at `packages/server/src/utils/constants.ts:40`.

### Attack Chain

1. Attacker obtains a credential ID (via Finding 2 / public chatflow leak, or enumeration)
2. Attacker calls `POST /api/v1/oauth2-credential/refresh/:credentialId` (no auth required)
3. Server decrypts credential, sends refresh request to OAuth provider with user's `client_secret`
4. Server returns the new `access_token` in the response to the attacker
5. Attacker uses the token to access the victim's connected service (Google, Microsoft, etc.)

### Docker Validation

`POST /api/v1/oauth2-credential/refresh/fake-uuid` returns `{"message":"Credential not found"}` (not 401 Unauthorized), proving the endpoint processes the request without authentication.

### Impact

- OAuth2 access token theft for any connected service
- Full access to the victim's third-party accounts (Google, Microsoft, GitHub, etc.)
- Client secret transmitted to OAuth provider during refresh
- Can also be used for DoS by exhausting refresh token quota

### Suggested Fix

Remove the refresh endpoint from `WHITELIST_URLS` and require authentication:

```typescript
// Remove from WHITELIST_URLS in constants.ts
// Add authentication check in the route handler
```

---

## Credits

- Shinobi Security - https://github.com/shinobisecurity

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-qgvm-j2hm-6m38
- https://github.com/FlowiseAI/Flowise
