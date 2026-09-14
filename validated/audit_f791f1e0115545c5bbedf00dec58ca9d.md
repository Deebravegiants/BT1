### Title
LDAP-backed role/authorization changes are not applied to already-established sessions and API tokens until the next periodic sync - (File: `core/sessions/ldapauth/sync.go`)

### Summary
The Bitnami/GitLab advisory describes a bug class where role/authorization changes made by an administrator were not propagated to already-established authorization state, letting a user retain permissions they should have lost. The chainlink LDAP authentication provider caches a user's role in the `ldap_sessions` and `ldap_user_api_tokens` tables at login time, and this cache is only refreshed by a periodic background sync (`LDAPServerStateSyncer.Work`). Between sync runs, a user whose upstream LDAP group membership is downgraded (or removed from the Admin/Edit group) keeps their previously-cached elevated role for every request authenticated via the existing session cookie or API token.

### Finding Description
`AuthorizedUserWithSession` for LDAP reads the user's role directly out of the local `ldap_sessions` table rather than the upstream LDAP directory: [1](#0-0) 

Likewise, API token authentication for LDAP-backed nodes is served from a similarly cached `ldap_user_api_tokens` table (role stored at token issuance time), not verified live against the LDAP server.

These caches are reconciled only by `LDAPServerStateSyncer.Work`, which runs on a `UpstreamSyncInterval` ticker and additionally is throttled by an optional `UpstreamSyncRateLimit`: [2](#0-1) 

When the sync does run, it rebuilds `upstreamUserStateMap` from current LDAP group membership and only then issues a bulk `UPDATE ldap_sessions SET user_role = CASE ... END` / `UPDATE ldap_user_api_tokens SET user_role = CASE ... END` for existing session/token rows: [3](#0-2) 

Until that update runs, `AuthorizedUserWithSession` and the API-token lookup path continue to return the stale (previously higher) role, which is then trusted directly by the RBAC middleware (`RequiresAdminRole`, `RequiresEditRole`, `RequiresRunRole`) to gate `/v2/*` admin/edit endpoints: [4](#0-3) [5](#0-4) 

This is functionally the same bug class as CVE-2020-10083: an authorization change made on the source-of-truth (LDAP group membership) is not applied to a still-live, previously-authenticated session/token, so the stale cached permission continues to be honored by the API gateway.

### Impact Explanation
A user who is demoted from Admin/Edit to a lower role (or removed entirely) in the upstream LDAP directory retains their old elevated role for any existing session cookie or previously issued API token until the next `UpstreamSyncInterval` tick (and optional `UpstreamSyncRateLimit` delay) elapses. During that window they can continue to perform admin-only actions (user management, fund transfers, key operations) or edit-role actions (bridge/external-initiator management) that should have been revoked. This is a privilege-persistence / authorization-bypass issue rather than a full account takeover, but it directly maps to "insecure permissions... authorization changes were not being applied" from the reference advisory.

### Likelihood Explanation
This only affects deployments configured with the LDAP `AuthenticationProviderName` (`core/sessions/authentication.go`), and requires an admin to have actually revoked/downgraded a user's LDAP role while that user retains a live session or API token — a realistic operational scenario (e.g., offboarding, incident response demoting a compromised/insider account). The exposure window is directly controlled by `UpstreamSyncInterval`/`UpstreamSyncRateLimit` config values, so likelihood scales with how infrequently an operator has configured the sync to run; I was not able to fully confirm the default value of `UpstreamSyncInterval` from the docs before running out of search budget, so the concrete default exposure window is unverified.

### Recommendation
- On revocation/role-downgrade intent, don't rely solely on the periodic sync: allow admins to force an immediate resync, or invalidate/downgrade all cached `ldap_sessions`/`ldap_user_api_tokens` entries for a given email as soon as a relevant change is detected.
- Consider re-validating role against LDAP (or at least reducing `UpstreamSyncInterval`) for privileged (Admin) operations specifically, since those carry the highest impact if stale.
- Document the authorization propagation delay clearly for operators so they understand that session/token revocation is not immediate under LDAP mode.

### Proof of Concept
1. Configure the node with `AuthenticationProviderName = "ldap"` and a non-trivial `UpstreamSyncInterval` (e.g., 5+ minutes).
2. User `alice@example.com` is a member of the upstream LDAP Admin group; she logs in, receiving a session whose role is cached as `admin` in `ldap_sessions` (`core/sessions/ldapauth/ldap.go:396-457`).
3. An LDAP administrator removes `alice` from the Admin group (demotes her to `view`).
4. Immediately after removal (before the next `LDAPServerStateSyncer.Work` tick), `alice` reuses her existing session cookie to call an admin-only endpoint, e.g. `PATCH /v2/users` (role update) or `POST /v2/transfers`.
5. `AuthenticateBySession` → `AuthorizedUserWithSession` returns the stale cached `admin` role from `ldap_sessions`, and `RequiresAdminRole` allows the request through, despite her upstream permissions already having been revoked.

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

**File:** core/sessions/ldapauth/sync.go (L76-116)
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

**File:** core/web/router.go (L245-257)
```go
	authv2 := r.Group("/v2", auth.Authenticate(app.AuthenticationProvider(),
		auth.AuthenticateByToken,
		auth.AuthenticateBySession,
	))
	{
		uc := UserController{app}
		authv2.GET("/users", auth.RequiresAdminRole(uc.Index))
		authv2.POST("/users", auth.RequiresAdminRole(uc.Create))
		authv2.PATCH("/users", auth.RequiresAdminRole(uc.UpdateRole))
		authv2.DELETE("/users/:email", auth.RequiresAdminRole(uc.Delete))
		authv2.PATCH("/user/password", uc.UpdatePassword)
		authv2.POST("/user/token", uc.NewAPIToken)
		authv2.POST("/user/token/delete", uc.DeleteAPIToken)
```
