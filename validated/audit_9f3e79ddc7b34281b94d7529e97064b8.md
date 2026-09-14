## Analysis: Ghost Session analog in Chainlink LDAP/OIDC authentication

The Bludit CVE describes a **mediation failure**: sessions stay valid because the system trusts a cached authentication decision instead of re-checking the authoritative user store on each request. Chainlink's LDAP and OIDC `AuthenticationProvider` implementations have the same architectural pattern.

### Title
Stale local session cache in LDAP/OIDC authenticators allows revoked users to retain full access until the next periodic upstream sync ("Ghost Session") - (File: `core/sessions/ldapauth/ldap.go`)

### Summary
For LDAP- and OIDC-backed Chainlink nodes, `AuthorizedUserWithSession` validates a request purely against a locally cached `ldap_sessions`/`oidc_sessions` table row, without contacting the upstream identity provider on each request. Revocation of a user's group membership (or deletion of the local admin fallback account) is only synchronized into that cache by a background job that runs on a configurable interval, and `DeleteUser` is explicitly unsupported for these providers. Between sync cycles, a removed/revoked user's session (and cached API token) remains fully authorized.

### Finding Description
`ldapAuthenticator.AuthorizedUserWithSession` looks up the session solely in the `ldap_sessions` table and only checks a locally stored expiry timestamp — it never re-queries the LDAP directory to confirm the user is still a member of an authorized group: [1](#0-0) 

Revocation is instead handled asynchronously by `LDAPServerStateSyncer.Work`, gated by `UpstreamSyncInterval` (and additionally throttled by `UpstreamSyncRateLimit`), which only purges `ldap_sessions`/`ldap_user_api_tokens` rows for users no longer present upstream when it actually executes: [2](#0-1) [3](#0-2) 

Compounding this, `DeleteUser` is a no-op for LDAP (identical for OIDC), meaning the Chainlink node itself has no direct/immediate revocation mechanism — the only path to kill a live session for a removed user is this periodic background sync: [4](#0-3) 

The OIDC authenticator exhibits the identical pattern — `AuthorizedUserWithSession` trusts the cached `oidc_sessions` row and its own `created_at + SessionTimeout` expiry, with no revalidation against the identity provider, and `DeleteUser` is likewise unsupported: [5](#0-4) [6](#0-5) 

These `AuthorizedUserWithSession` results feed directly into the gateway/API request-authentication middleware (`AuthenticateBySession`, `AuthenticateGQL`), so a stale session grants full REST/GraphQL API access: [7](#0-6) [8](#0-7) 

Contrast this with the `localauth` provider, where `DeleteUser` deletes the `users` row and sessions cascade-delete via a DB foreign-key constraint tied to `email`, so revocation is immediate there: [9](#0-8) 

### Impact Explanation
An LDAP/OIDC-authenticated user whose access is revoked upstream (removed from an authorized group, disabled, or terminated) retains a fully valid, admin-capable Chainlink node session/API token for as long as the sync interval takes to run (and can be delayed further by `UpstreamSyncRateLimit`). Because the node has no synchronous revocation path (`DeleteUser` returns `ErrNotSupported`), an operator cannot immediately kill this access — a config-only remediation. This matches the report's "persistent access despite deprovisioning" class of Broken Access Control, and on a node exposing job management, key/secret access, and fund-moving operations, this is a high-impact unauthorized-access window.

### Likelihood Explanation
This affects any deployment using `LDAPAuth` or `OIDCAuth` (`core/sessions/authentication.go` constants), which are supported, documented authentication providers, not a mocked-only or test-only path. The gap is deterministic and depends only on configuration (`UpstreamSyncInterval`), not on any race condition or attacker sophistication — any offboarded/attacker-compromised account exploits it automatically simply by continuing to use its existing session/token until the next sync.

### Recommendation
- For LDAP/OIDC providers, revalidate the user's continued authorization (or at minimum a much shorter TTL / on-demand recheck) rather than relying purely on the cached session table state for the full `SessionTimeout` duration.
- Implement (or expose) synchronous session/token revocation for LDAP/OIDC providers instead of `ErrNotSupported`, so an admin action to remove access is not solely dependent on the periodic sync job.
- Consider triggering an immediate `Work()` sync pass when critical authorization state changes are expected, and clearly document the exposure window created by `UpstreamSyncInterval`/`UpstreamSyncRateLimit`.

### Proof of Concept
1. Configure a Chainlink node with `LDAPAuth` (or `OIDCAuth`) and a non-trivial `UpstreamSyncInterval`.
2. A user authenticates via `/sessions`, obtaining a session cookie backed by a row in `ldap_sessions` (`ldapAuthenticator.CreateSession`), per `core/sessions/ldapauth/ldap.go:392-457`.
3. The administrator removes the user from the authorized LDAP group (or disables the account) directly in the directory — there is no Chainlink-side `DeleteUser` support (`ErrNotSupported`).
4. Before `LDAPServerStateSyncer.Work` next executes (bounded by `UpstreamSyncInterval`/`UpstreamSyncRateLimit`), the attacker replays the still-valid session cookie against any authenticated route (e.g., `/v2/keys`, GraphQL admin mutations).
5. `AuthenticateBySession` → `ldapAuthenticator.AuthorizedUserWithSession` validates purely against the cached `ldap_sessions` row and returns success, granting full API access despite the account being revoked upstream.

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

**File:** core/sessions/ldapauth/ldap.go (L375-378)
```go
// DeleteUser is not supported for read only LDAP
func (l *ldapAuthenticator) DeleteUser(ctx context.Context, email string) error {
	return sessions.ErrNotSupported
}
```

**File:** core/sessions/ldapauth/sync.go (L56-116)
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

func (l *LDAPServerStateSyncer) Close() error {
	close(l.stopCh)
	<-l.done
	return nil
}

func (l *LDAPServerStateSyncer) run() {
	defer close(l.done)
	ctx, cancel := l.stopCh.NewCtx()
	defer cancel()
	ticker := time.NewTicker(l.config.UpstreamSyncInterval().Duration())
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			l.Work(ctx)
		}
	}
}

func (l *LDAPServerStateSyncer) Work(ctx context.Context) {
	// Purge expired ldap_sessions and ldap_user_api_tokens
	recordCreationStaleThreshold := l.config.SessionTimeout().Before(time.Now())
	err := l.deleteStaleSessions(ctx, recordCreationStaleThreshold)
	if err != nil {
		l.lggr.Error("unable to expire local LDAP sessions: ", err)
	}
	recordCreationStaleThreshold = l.config.UserAPITokenDuration().Before(time.Now())
	err = l.deleteStaleAPITokens(ctx, recordCreationStaleThreshold)
	if err != nil {
		l.lggr.Error("unable to expire user API tokens: ", err)
	}

	// Optional rate limiting check to limit the amount of upstream LDAP server queries performed
	if !l.config.UpstreamSyncRateLimit().IsInstant() {
		if !time.Now().After(l.nextSyncTime) {
			return
		}

		// Enough time has elapsed to sync again, store the time for when next sync is allowed and begin sync
		l.nextSyncTime = time.Now().Add(l.config.UpstreamSyncRateLimit().Duration())
	}

	l.lggr.Info("Begin Upstream LDAP provider state sync after checking time against config UpstreamSyncInterval and UpstreamSyncRateLimit")
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

**File:** core/sessions/oidcauth/oidc.go (L349-391)
```go
// AuthorizedUserWithSession will return the API user associated with the Session ID if it
// exists and hasn't expired
func (oi *oidcAuthenticator) AuthorizedUserWithSession(ctx context.Context, sessionID string) (clsessions.User, error) {
	if len(sessionID) == 0 {
		return clsessions.User{}, errors.New("session ID cannot be empty")
	}
	var foundUser clsessions.User
	err := sqlutil.TransactDataSource(ctx, oi.ds, nil, func(tx sqlutil.DataSource) error {
		// Query the oidc_sessions table for given session ID, user role and email are saved after the id claims is provided and validated
		var foundSession struct {
			UserEmail string
			UserRole  clsessions.UserRole
			Valid     bool
		}
		if err := tx.GetContext(ctx, &foundSession,
			"SELECT user_email, user_role, created_at + $2 >= now() as valid FROM oidc_sessions WHERE id = $1",
			sessionID, oi.config.SessionTimeout().Duration(),
		); err != nil {
			if errors.Is(err, sql.ErrNoRows) {
				return clsessions.ErrUserSessionExpired
			}
			return err
		}
		if !foundSession.Valid {
			// Sessions expired, purge
			return clsessions.ErrUserSessionExpired
		}
		foundUser = clsessions.User{
			Email: foundSession.UserEmail,
			Role:  foundSession.UserRole,
		}
		return nil
	})
	if err != nil {
		if errors.Is(err, clsessions.ErrUserSessionExpired) {
			if _, execErr := oi.ds.ExecContext(ctx, "DELETE FROM oidc_sessions WHERE id = $1", sessionID); execErr != nil {
				oi.lggr.Errorf("error purging stale OIDC session: %v", execErr)
			}
		}
		return clsessions.User{}, err
	}
	return foundUser, nil
}
```

**File:** core/sessions/oidcauth/oidc.go (L393-396)
```go
// DeleteUser is not supported for read only OIDC
func (oi *oidcAuthenticator) DeleteUser(ctx context.Context, email string) error {
	return clsessions.ErrNotSupported
}
```

**File:** core/web/auth/auth.go (L52-71)
```go
// AuthenticateBySession authenticates the request by the session cookie.
//
// Implements authMethod
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

**File:** core/web/auth/gql.go (L20-48)
```go
// AuthenticateGQL middleware checks the session cookie for a user and sets it
// on the request context if it exists. It is the responsibility of each resolver
// to validate whether it requires an authenticated user.
//
// We currently only support GQL authentication by session cookie.
func AuthenticateGQL(authenticator Authenticator, lggr logger.Logger) gin.HandlerFunc {
	return func(c *gin.Context) {
		ctx := c.Request.Context()
		session := sessions.Default(c)
		sessionID, ok := session.Get(SessionIDKey).(string)
		if !ok {
			return
		}

		user, err := authenticator.AuthorizedUserWithSession(ctx, sessionID)
		if err != nil {
			if errors.Is(err, clsessions.ErrUserSessionExpired) {
				lggr.Warnw("Failed to authenticate session", "err", err)
			} else {
				lggr.Errorw("Failed call to AuthorizedUserWithSession, unable to get user", "err", err)
			}
			return
		}

		ctx = WithGQLAuthenticatedSession(c.Request.Context(), user, sessionID)

		c.Request = c.Request.WithContext(ctx)
	}
}
```

**File:** core/sessions/localauth/orm.go (L109-118)
```go
// DeleteUser will delete an API User and sessions by email.
func (o *orm) DeleteUser(ctx context.Context, email string) error {
	return sqlutil.TransactDataSource(ctx, o.ds, nil, func(tx sqlutil.DataSource) error {
		// session table rows are deleted on cascade through the user email constraint
		if _, err := tx.ExecContext(ctx, "DELETE FROM users WHERE email = $1", email); err != nil {
			return err
		}
		return nil
	})
}
```
