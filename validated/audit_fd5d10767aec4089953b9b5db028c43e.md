## Title
Stale Cached Role Authorization in LDAP-Backed Sessions and API Tokens After Upstream Privilege Revocation - (File: `core/sessions/ldapauth/ldap.go`, `core/sessions/ldapauth/sync.go`)

## Summary
When the WebServer authentication method is `ldap`, Chainlink caches a user's `role` in the `ldap_sessions` and `ldap_user_api_tokens` tables at login/token-issuance time, and every subsequent authorization decision trusts this cached value instead of re-checking the upstream LDAP group membership. Propagation of revoked/reduced privileges to already-issued sessions and tokens depends entirely on a background sync task (`LDAPServerStateSyncer`) that is **disabled by default** (`UpstreamSyncInterval = '0s'`), so a demoted/removed admin can keep exercising admin-level API/WebUI actions for the full remaining session or API-token lifetime.

## Finding Description
`ldapAuthenticator.CreateSession` queries the LDAP group membership once at login via `FindUser`/`ldapGroupMembersListToUser`, then persists the resolved role into the `ldap_sessions` table:
<cite repo="AYontt/chainlink--018" path="core/sessions/ldapauth/ldap.go" start="413="440" end="452" /> [1](#0-0) 

All subsequent request authorization calls `AuthorizedUserWithSession`, which purely does a time-bound `SELECT` against the cached `user_role` column — it never re-queries LDAP: [2](#0-1) 

This cached `role` is set into the Gin context by `AuthenticateBySession` and then trusted by every role gate (`RequiresRunRole`, `RequiresEditRole`, `RequiresAdminRole`): [3](#0-2) [4](#0-3) 

The only mechanism that reconciles cached roles with the authoritative upstream LDAP directory is `LDAPServerStateSyncer.Work`, which re-queries each configured group and issues a bulk `UPDATE ldap_sessions/ldap_user_api_tokens SET user_role = ...`: [5](#0-4) 

However, this task is only run **once at process startup** unless an operator explicitly configures a non-zero interval — the documented default is `'0s'`, which disables periodic syncing entirely: [6](#0-5) [7](#0-6) 

Neither `CreateSession` nor `DeleteUserSession` for the LDAP path triggers this reconciliation for *other* active sessions belonging to the same or other users — each only manages the single session being created/deleted: [8](#0-7) 

The exposure is compounded for long-lived API tokens: `UserAPITokenDuration` defaults to `240h0m0s` (10 days), and `FindUserByAPIToken`-style lookups for LDAP tokens are documented as relying on the same cached `user_role`, synced "via the `UpstreamSyncInterval` config" — which, again, is disabled by default. [9](#0-8) 

This mirrors the reported pyLoad bug class exactly (CWE-613): authorization state (`role`) is cached at authentication time and trusted for the lifetime of the credential, while the privilege-revocation channel (admin removing the user from an LDAP group) is a fire-and-forget operation on the external directory with no corresponding invalidation of already-issued Chainlink sessions/tokens.

## Impact Explanation
An operator who removes/downgrades a user's LDAP group membership (e.g., removing them from the `NodeAdmins` group) cannot immediately revoke that user's access on the Chainlink node. As long as `UpstreamSyncInterval` remains at its documented default (`0s`), the demoted user retains full admin-level WebUI/API authorization — including user management, bridge/job management, and key/credential operations gated by `RequiresAdminRole` — until their session naturally expires (`SessionTimeout`, default `15m0s`) or, for API tokens, up to `UserAPITokenDuration` (default `240h0m0s`, i.e. 10 days). This is a concrete authentication/role-bypass condition matching the "Accept" criteria: continued privileged action after revocation.

## Likelihood Explanation
This requires no attacker sophistication beyond being a previously-authorized user whose privileges get revoked by an admin while the deployment uses the LDAP authentication provider with default sync settings (which the shipped config documents as the default). Because the vulnerable condition is the *default* configuration (`UpstreamSyncInterval = '0s'`), any LDAP-authenticated deployment that hasn't explicitly opted into periodic syncing is affected, making likelihood high in realistic operational settings.

## Recommendation
- Re-verify role/permission against the authoritative source (or force session/token invalidation) on every privileged request rather than trusting the DB-cached `user_role`, or
- Make `UpstreamSyncInterval` mandatory/non-zero by default (or emit a startup warning) so revocation propagates promptly, and
- Trigger an immediate `Work()`-style reconciliation pass whenever an admin-initiated user/role management action occurs, and consider actively invalidating (deleting) `ldap_sessions`/`ldap_user_api_tokens` rows for users no longer present in any configured role group, similar to how `localauth.orm.UpdateRole` deletes the user's `sessions` rows on role change.

## Proof of Concept
1. Configure `WebServer.AuthenticationMethod = 'ldap'` with default `WebServer.LDAP.UpstreamSyncInterval = '0s'`.
2. User `alice@example.com` is a member of the `NodeAdmins` LDAP group; she logs in via `CreateSession`, which resolves her role to `admin` and stores it in `ldap_sessions` (`core/sessions/ldapauth/ldap.go:437-452`).
3. Admin removes `alice@example.com` from the `NodeAdmins` group in the upstream LDAP directory (no Chainlink-side action taken).
4. Alice continues issuing admin-gated requests (e.g., `PATCH /v2/users`); `AuthenticateBySession` → `AuthorizedUserWithSession` (`core/sessions/ldapauth/ldap.go:342-373`) returns her stale cached `role=admin` from `ldap_sessions`, and `RequiresAdminRole` (`core/web/auth/auth.go:237-253`) allows the request.
5. Because `LDAPServerStateSyncer.run()` never starts (interval is `0s`, only a one-time `Work(ctx)` at boot per `core/sessions/ldapauth/sync.go:56-68`), Alice's admin access persists until her session expires (`SessionTimeout`, default 15 minutes) or, if using an LDAP-issued API token, up to `UserAPITokenDuration` (default 10 days).

### Citations

**File:** core/sessions/ldapauth/ldap.go (L342-373)
```go
// AuthorizedUserWithSession will return the API user associated with the Session ID if it
// exists and hasn't expired, and update session's LastUsed field. The state of the upstream LDAP server
// is polled and synced at the defined interval via a SleeperTask
func (l *ldapAuthenticator) AuthorizedUserWithSession(ctx context.Context, sessionID string) (sessions.User, error) {
	if len(sessionID) == 0 {
		return sessions.User{}, errors.New("session ID cannot be empty")
	}
	// Query the ldap_sessions table for given session ID, user role and email are cached so
	// no further upstream LDAP query is performed
	var foundSession struct {
		UserEmail string
		UserRole  sessions.UserRole
		Valid     bool
	}
	if err := l.ds.GetContext(ctx, &foundSession,
		"SELECT user_email, user_role, created_at + $2 >= now() as valid FROM ldap_sessions WHERE id = $1",
		sessionID, l.config.SessionTimeout().Duration(),
	); err != nil {
		return sessions.User{}, sessions.ErrUserSessionExpired
	}
	if !foundSession.Valid {
		// Sessions expired, purge
		if _, execErr := l.ds.ExecContext(ctx, "DELETE FROM ldap_sessions WHERE id = $1", sessionID); execErr != nil {
			l.lggr.Errorf("error purging stale ldap session: %v", execErr)
		}
		return sessions.User{}, sessions.ErrUserSessionExpired
	}
	return sessions.User{
		Email: foundSession.UserEmail,
		Role:  foundSession.UserRole,
	}, nil
}
```

**File:** core/sessions/ldapauth/ldap.go (L380-384)
```go
// DeleteUserSession removes an ldapSession table entry by ID
func (l *ldapAuthenticator) DeleteUserSession(ctx context.Context, sessionID string) error {
	_, err := l.ds.ExecContext(ctx, "DELETE FROM ldap_sessions WHERE id = $1", sessionID)
	return err
}
```

**File:** core/sessions/ldapauth/ldap.go (L437-452)
```go
	// Save session, user, and role to database. Given a session ID for future queries, the LDAP server will not be queried
	// Sessions are set to expire after the duration + creation date elapsed, and are synced on an interval against the upstream
	// LDAP server
	session := sessions.NewSession()
	_, err = l.ds.ExecContext(
		ctx,
		"INSERT INTO ldap_sessions (id, user_email, user_role, localauth_user, created_at) VALUES ($1, $2, $3, $4, now())",
		session.ID,
		strings.ToLower(sr.Email),
		foundUser.Role,
		isLocalUser,
	)
	if err != nil {
		l.lggr.Errorf("unable to create new session in ldap_sessions table %v", err)
		return "", fmt.Errorf("error creating local LDAP session: %w", err)
	}
```

**File:** core/web/auth/auth.go (L55-71)
```go
func AuthenticateBySession(c *gin.Context, authr Authenticator) error {
	ctx := c.Request.Context()
	session := sessions.Default(c)
	sessionID, ok := session.Get(SessionIDKey).(string)
	if !ok {
		return auth.ErrorAuthFailed
	}

	user, err := authr.AuthorizedUserWithSession(ctx, sessionID)
	if err != nil {
		return err
	}

	c.Set(SessionUserKey, &user)

	return nil
}
```

**File:** core/web/auth/auth.go (L236-253)
```go
// RequiresAdminRole extracts the user object from the context, and asserts the user's role is 'admin'
func RequiresAdminRole(handler func(*gin.Context)) func(*gin.Context) {
	return func(c *gin.Context) {
		user, ok := GetAuthenticatedUser(c)
		if !ok {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("not a valid session"))
			return
		}
		if user.Role != clsessions.UserRoleAdmin {
			c.Abort()
			addForbiddenErrorHeaders(c, "admin", string(user.Role), user.Email)
			jsonAPIError(c, http.StatusForbidden, errors.New("Forbidden"))
			return
		}
		handler(c)
	}
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

**File:** core/sessions/ldapauth/sync.go (L245-275)
```go
		// For each user session row, update role to match state of user map from upstream source
		var queryWhenClause strings.Builder
		emailValues := []any{}
		// Prepare CASE WHEN query statement with parameterized argument $n placeholders and matching role based on index
		for email, user := range upstreamUserStateMap {
			// Only build on SET CASE statement per local session and API token role, not for each upstream user value
			_, sessionOk := existingSessionsMap[email]
			_, tokenOk := existingAPITokensMap[email]
			if !sessionOk && !tokenOk {
				continue
			}
			emailValues = append(emailValues, email)
			fmt.Fprintf(&queryWhenClause, "WHEN user_email = $%d THEN '%s' ", len(emailValues), user.Role)
		}

		// If there are remaining user entries to update
		if len(emailValues) != 0 {
			// Set new role state for all rows in single Exec
			query := fmt.Sprintf("UPDATE ldap_sessions SET user_role = CASE %s ELSE user_role END", &queryWhenClause)
			_, err = tx.ExecContext(ctx, query, emailValues...)
			if err != nil {
				return err
			}

			// Update role of API tokens as well
			query = fmt.Sprintf("UPDATE ldap_user_api_tokens SET user_role = CASE %s ELSE user_role END", &queryWhenClause)
			_, err = tx.ExecContext(ctx, query, emailValues...)
			if err != nil {
				return err
			}
		}
```

**File:** core/config/docs/core.toml (L264-269)
```text
# UserApiTokenEnabled enables the users to issue API tokens with the same access of their role
UserApiTokenEnabled = false # Default
# UserAPITokenDuration is the duration of time an API token is active for before expiring
UserAPITokenDuration = '240h0m0s' # Default
# UpstreamSyncInterval is the interval at which the background LDAP sync task will be called. A '0s' value disables the background sync being run on an interval. This check is already performed during login/logout actions, all sessions and API tokens stored in the local ldap tables are updated to match the remote server
UpstreamSyncInterval = '0s' # Default
```
