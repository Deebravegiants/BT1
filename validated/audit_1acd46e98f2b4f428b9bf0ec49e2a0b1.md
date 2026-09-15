Audit Report

## Title
Disabled LDAP users retain full API access via previously issued API tokens - (File: `core/sessions/ldapauth/ldap.go`)

## Summary
The LDAP authentication provider enforces the "is active" check in `FindUser` (used for interactive login) via `validateUsersActive`, but `FindUserByAPIToken` (used by the API token authentication middleware) performs no equivalent check — it only validates token existence and expiry against the local `ldap_user_api_tokens` cache. This allows a user deactivated on the upstream LDAP server, or removed from all authorized groups, to continue authenticating with a previously issued API token until the token expires or an upstream sync reaper cycle happens to purge it.

## Finding Description
`FindUser` explicitly re-validates the user's active status upstream before allowing a session to be created: [1](#0-0) 

`FindUserByAPIToken`, by contrast, only queries the local `ldap_user_api_tokens` table for token existence/expiry and returns the cached role without any upstream active-status re-check: [2](#0-1) 

The web auth middleware `AuthenticateByToken` calls `FindUserByAPIToken` directly and, upon a valid (unexpired) row, sets the authenticated session user with no additional active/role revalidation: [3](#0-2) 

The only mechanism that can revoke a deactivated user's token is `LDAPServerStateSyncer.Work`, which re-queries LDAP group membership/active status and purges `ldap_user_api_tokens` rows for emails no longer present in `upstreamUserStateMap`: [4](#0-3) [5](#0-4) 

Crucially, this reaper only runs on a recurring timer if `UpstreamSyncInterval` is configured to a non-zero value; otherwise `Work` executes exactly once at node startup and never again: [6](#0-5) 

This confirms the claim precisely: token-based auth (`FindUserByAPIToken`) lacks the active-status enforcement present in session-based auth (`FindUser`), and the periodic reaper is the only backstop, which is itself dependent on operator configuration of `UpstreamSyncInterval`.

## Impact Explanation
This maps to the in-scope "node API authentication or role bypass" impact category. An LDAP-backed node operator who disables a compromised or departed user's account has no guarantee that access is actually revoked — a previously issued API token continues to authenticate as that user's cached role (Admin/Edit/Run/View) through `webauth.AuthenticateByToken`, permitting continued access to role-gated node management endpoints until token expiry (`UserAPITokenDuration`) or a reaper cycle purges the stale row.

## Likelihood Explanation
This affects only deployments using `LDAPAuth` with `UserApiTokenEnabled` and a previously issued, unexpired API token. Exploitation requires no special network position or elevated privilege beyond simple possession of an already-valid token — a straightforward and realistic scenario, especially since the reaper only runs periodically when `UpstreamSyncInterval` is explicitly configured non-zero; with the default/instant setting, the reaper never re-runs after startup, making the exposure window effectively unbounded until token expiry.

## Recommendation
Add an active-status check to `FindUserByAPIToken`, mirroring `validateUsersActive` as used in `FindUser`, so deactivated/removed upstream users are rejected at token-auth time rather than only at login. Additionally, consider enforcing a mandatory minimum re-sync interval for `LDAPServerStateSyncer.Work` rather than allowing it to run only once at startup when `UpstreamSyncInterval` is unset.

## Proof of Concept
1. Configure Chainlink with `LDAPAuth`, `UserApiTokenEnabled = true`, and leave `UpstreamSyncInterval` at its default/zero (instant) value.
2. As a normal LDAP user, create an API token via `CreateAndSetAuthToken`, producing a row in `ldap_user_api_tokens`.
3. Deactivate that user upstream (unset `ActiveAttribute`) or remove them from all role groups.
4. Send authenticated HTTP requests using the previously issued `APIKey`/`APISecret` headers against an endpoint protected by `webauth.AuthenticateByToken`.
5. Observe requests continue to succeed with the user's previously assigned role, since `FindUserByAPIToken` never re-checks active status and the reaper (`LDAPServerStateSyncer.Work`) does not re-run without a configured `UpstreamSyncInterval`.

### Citations

**File:** core/sessions/ldapauth/ldap.go (L131-142)
```go
	// First query for user "is active" property if defined
	usersActive, err := l.validateUsersActive([]string{email})
	if err != nil {
		if errors.Is(err, ErrUserNotInUpstream) {
			return sessions.User{}, ErrUserNotInUpstream
		}
		l.lggr.Errorf("error in validateUsers call: %v", err)
		return sessions.User{}, errors.New("error running query to validate user active")
	}
	if !usersActive[0] {
		return sessions.User{}, errors.New("user not active")
	}
```

**File:** core/sessions/ldapauth/ldap.go (L204-236)
```go
// FindUserByAPIToken retrieves a possible stored user and role from the ldap_user_api_tokens table store
func (l *ldapAuthenticator) FindUserByAPIToken(ctx context.Context, apiToken string) (sessions.User, error) {
	if !l.config.UserApiTokenEnabled() {
		return sessions.User{}, errors.New("API token is not enabled ")
	}

	// Query the ldap user API token table for given token, user role and email are cached so
	// no further upstream LDAP query is performed, sessions and tokens are synced against the upstream server
	// via the UpstreamSyncInterval config and reaper.go sync implementation
	var foundUserToken struct {
		UserEmail string
		UserRole  sessions.UserRole
		Valid     bool
	}
	err := l.ds.GetContext(ctx, &foundUserToken,
		"SELECT user_email, user_role, created_at + $2 >= now() as valid FROM ldap_user_api_tokens WHERE token_key = $1",
		apiToken, l.config.UserAPITokenDuration().Duration(),
	)
	if err != nil {
		return sessions.User{}, err
	}
	if !foundUserToken.Valid { // API Token expired, purge
		if _, execErr := l.ds.ExecContext(ctx, "DELETE FROM ldap_user_api_tokens WHERE token_key = $1", apiToken); execErr != nil {
			l.lggr.Errorf("error purging stale ldap API token session: %v", execErr)
		}
		return sessions.User{}, sessions.ErrUserSessionExpired
	}

	return sessions.User{
		Email: foundUserToken.UserEmail,
		Role:  foundUserToken.UserRole,
	}, nil
}
```

**File:** core/web/auth/auth.go (L75-112)
```go
// AuthenticateByToken authenticates a User by their API token.
//
// Implements authMethod
func AuthenticateByToken(c *gin.Context, authr Authenticator) error {
	ctx := c.Request.Context()
	token := &auth.Token{
		AccessKey: c.GetHeader(APIKey),
		Secret:    c.GetHeader(APISecret),
	}
	if token.AccessKey == "" {
		return auth.ErrorAuthFailed
	}

	if token.Secret == "" {
		return auth.ErrorAuthFailed
	}

	// We need to first load the user row so we can compare tokens using the stored salt
	user, err := authr.FindUserByAPIToken(ctx, token.AccessKey)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) || errors.Is(err, clsessions.ErrUserSessionExpired) {
			return auth.ErrorAuthFailed
		}
		return err
	}

	ok, err := clsessions.AuthenticateUserByToken(token, &user)
	if err != nil {
		return err
	}
	if !ok {
		return auth.ErrorAuthFailed
	}

	c.Set(SessionUserKey, &user)

	return nil
}
```

**File:** core/sessions/ldapauth/sync.go (L56-68)
```go
func (l *LDAPServerStateSyncer) Start(ctx context.Context) error {
	// If enabled, start a background task that calls the Sync/Work function on an
	// interval without needing an auth event to trigger it
	// Use IsInstant to check 0 value to omit functionality.
	if !l.config.UpstreamSyncInterval().IsInstant() {
		l.lggr.Info("LDAP Config UpstreamSyncInterval is non-zero, sync functionality will be called on a timer, respecting the UpstreamSyncRateLimit value")
		go l.run()
	} else {
		// Ensure upstream server state is synced on startup manually if interval check not set
		l.Work(ctx)
	}
	return nil
}
```

**File:** core/sessions/ldapauth/sync.go (L164-185)
```go
	// Preserve members as a map for future lookup
	upstreamUserStateMap := make(map[string]sessions.User)
	dedupedEmails := []string{}
	for _, user := range users {
		if _, ok := upstreamUserStateMap[user.Email]; !ok {
			upstreamUserStateMap[user.Email] = user
			dedupedEmails = append(dedupedEmails, user.Email)
		}
	}

	// For each unique user in list of active sessions, check for 'Is Active' property if defined in the config. Some LDAP providers
	// list group members that are no longer marked as active
	usersActiveFlags, err := l.validateUsersActive(dedupedEmails, conn)
	if err != nil {
		l.lggr.Error("Error validating supplied user list: ", err)
	}
	// Remove users in the upstreamUserStateMap source of truth who are part of groups but marked as deactivated/no-active
	for i, active := range usersActiveFlags {
		if !active {
			delete(upstreamUserStateMap, dedupedEmails[i])
		}
	}
```

**File:** core/sessions/ldapauth/sync.go (L214-243)
```go
		// Populate list of session emails present in the local session table but not in the upstream state
		emailsToPurge := []any{}
		for _, ldapSession := range existingSessions {
			if _, ok := upstreamUserStateMap[ldapSession.UserEmail]; !ok {
				emailsToPurge = append(emailsToPurge, ldapSession.UserEmail)
			}
		}
		// Likewise for API Tokens table
		apiTokenEmailsToPurge := []any{}
		for _, ldapSession := range existingAPITokens {
			if _, ok := upstreamUserStateMap[ldapSession.UserEmail]; !ok {
				apiTokenEmailsToPurge = append(apiTokenEmailsToPurge, ldapSession.UserEmail)
			}
		}

		// Remove any active sessions this user may have
		if len(emailsToPurge) > 0 {
			_, err = tx.ExecContext(ctx, "DELETE FROM ldap_sessions WHERE user_email = ANY($1)", pq.Array(emailsToPurge))
			if err != nil {
				return err
			}
		}

		// Remove any active API tokens this user may have
		if len(apiTokenEmailsToPurge) > 0 {
			_, err = tx.ExecContext(ctx, "DELETE FROM ldap_user_api_tokens WHERE user_email = ANY($1)", pq.Array(apiTokenEmailsToPurge))
			if err != nil {
				return err
			}
		}
```
