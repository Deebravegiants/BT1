### Title
Stale-session persistence after upstream deactivation in LDAP/OIDC session authorizers - ([File: core/sessions/ldapauth/ldap.go], [File: core/sessions/oidcauth/oidc.go])

### Summary
For the LDAP and OIDC authentication backends, `AuthorizedUserWithSession` validates a request solely against a locally cached `ldap_sessions` / `oidc_sessions` row (email, role, expiry), and does not re-check the upstream identity provider on each request. Revalidation against the upstream server (which would detect a suspended/deactivated/removed account) only happens on a separate periodic sync job. This mirrors the CVE-2017-1000135 bug class: a user whose upstream account/institution is suspended can keep using an already-issued session/token until the next sync cycle, rather than being immediately logged out or denied.

### Finding Description
`ldapAuthenticator.AuthorizedUserWithSession` looks up the session purely from the local `ldap_sessions` table, checking only expiry (`created_at + timeout >= now()`), and returns the cached `user_email`/`user_role` without contacting the LDAP server: [1](#0-0) 

The package-level doc comment for this file explicitly states that upstream state (including deactivation) is only reconciled by the periodic syncer, not per-request: [2](#0-1) 

The actual upstream revalidation and session/token purge for deactivated users is implemented in `LDAPServerStateSyncer.Work`, which runs on a background ticker at `UpstreamSyncInterval`, and additionally supports an `UpstreamSyncRateLimit` that can further throttle how often the sync executes: [3](#0-2) [4](#0-3) 

`validateUsersActive` is the mechanism that queries the upstream `ActiveAttribute` and removes deactivated users from `upstreamUserStateMap`, but this is only invoked from within `Work`, not from `AuthorizedUserWithSession`: [5](#0-4) 

The purge of stale sessions/tokens for users no longer present/active upstream happens inside the same `Work` sync transaction: [6](#0-5) 

The OIDC authenticator has the analogous design: `AuthorizedUserWithSession` only checks the local `oidc_sessions` table's cached role/email and expiry timestamp, with no per-request call back to the OIDC provider to confirm the account/session is still valid: [7](#0-6) 

Both authenticators are wired into the standard web/GraphQL session-auth middleware, which simply trusts whatever `AuthorizedUserWithSession` returns for the lifetime of the cached session row: [8](#0-7) [9](#0-8) 

### Impact Explanation
If an organization suspends/deactivates a user in the upstream LDAP directory or OIDC provider (e.g., due to termination or a security incident), that user's already-established Chainlink node web session or LDAP API token remains fully authorized until the next `UpstreamSyncInterval`/`UpstreamSyncRateLimit` cycle completes. Depending on operator configuration, this window can be arbitrarily long (the `IsInstant()` checks allow disabling both timers, in which case sync only runs once at node startup). During that window, a deactivated but still-connected user retains their previously granted role (potentially `admin`), allowing continued access to job management, key/secret-adjacent admin functionality, and other authenticated web/GraphQL APIs on the node — directly analogous to the Mahara CVE where suspended-institution users retained authenticated access.

### Likelihood Explanation
This is reachable by any legitimately-authenticated (but subsequently deactivated) user simply continuing to use their existing session cookie or LDAP API token — no additional privilege or attack complexity is required, and it depends entirely on operator-controlled sync interval settings, which is common in production LDAP/OIDC-integrated deployments.

### Recommendation
Add per-request (or short-TTL) freshness enforcement to `AuthorizedUserWithSession` for both `ldapauth` and `oidcauth`, such as checking a locally-tracked "last upstream verified at" timestamp with a low ceiling independent of the operator-configurable sync interval, or triggering an inline upstream active-status check when a session is near its cached staleness threshold. Alternatively, expose and default `UpstreamSyncInterval`/`UpstreamSyncRateLimit` to conservative values and document the exposure window explicitly, and ensure `Work` cannot be effectively disabled via `IsInstant()` without an explicit administrator acknowledgment of the risk.

### Proof of Concept
1. Configure a node with LDAP auth and `UpstreamSyncInterval` set to a large value (or `0`/instant, causing sync to run only once at startup).
2. A user with `admin` role in the LDAP group logs in via `CreateSession`, receiving a session cookie backed by an `ldap_sessions` row with cached `user_role = admin`.
3. An LDAP administrator removes/deactivates the user upstream (e.g., removes group membership or flips the `ActiveAttribute`).
4. Before the next sync tick (or indefinitely, if sync interval is instant/startup-only), the already-issued session continues to pass `AuthorizedUserWithSession` in [1](#0-0) , and the user keeps full `admin` access to the node's web/GraphQL API despite being deactivated upstream.

### Citations

**File:** core/sessions/ldapauth/ldap.go (L12-19)
```go
User session and roles are cached and revalidated with the upstream service at the interval defined in
the local LDAP config through the Application.sessionReaper implementation in reaper.go.

Changes to the upstream identity server will propagate through and update local tables (web sessions, API tokens)
by either removing the entries or updating the roles. This sync happens for every auth endpoint hit, and
via the defined sync interval. One goroutine is created to coordinate the sync timing in the New function

This implementation is read only; user mutation actions such as Delete are not supported.
```

**File:** core/sessions/ldapauth/ldap.go (L345-373)
```go
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

**File:** core/sessions/ldapauth/ldap.go (L644-656)
```go
// validateUsersActive performs an additional LDAP server query for the supplied emails, checking the
// returned user data for an 'active' property defined optionally in the config.
// Returns same length bool 'valid' array, indexed by sorted email
func (l *ldapAuthenticator) validateUsersActive(emails []string) ([]bool, error) {
	validUsers := make([]bool, len(emails))
	// If active attribute to check is not defined in config, skip
	if l.config.ActiveAttribute() == "" {
		// fill with valids
		for i := range emails {
			validUsers[i] = true
		}
		return validUsers, nil
	}
```

**File:** core/sessions/ldapauth/sync.go (L76-91)
```go
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
```

**File:** core/sessions/ldapauth/sync.go (L93-116)
```go
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

**File:** core/web/auth/gql.go (L25-48)
```go
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
