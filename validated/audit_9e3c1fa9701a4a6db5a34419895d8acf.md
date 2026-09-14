Confirmed: `NewLDAPServerStateSyncer` (`sync.go`) is only invoked from `ldap.go` and `application.go` as a background service that runs on `UpstreamSyncInterval` (default `0s`, i.e. disabled — a manual one-time `Work` call happens only at startup) or via `UpstreamSyncRateLimit`-gated periodic runs, but it is **not** triggered per-request. `AuthorizedUserWithSession` and `FindUserByAPIToken` only check local table expiry (`Valid` via `created_at + duration >= now()`), never re-checking the upstream LDAP "active" status. This confirms the analog below.

### Title
Deactivated ("suspended") LDAP user's existing session/API token still grants full authenticated access - ([File: core/sessions/ldapauth/ldap.go])

### Summary
The Sherlock report concerns a suspended `partyB` account still able to perform privileged actions because critical functions never re-check the account's suspended status, relying only on a status check done at a different entry point (quote opening). The chainlink LDAP authenticator has the same class of bug: the "active" status of a user is validated only inside `FindUser`/`ListUsers` (used at login time), while the actual per-request authorization paths `AuthorizedUserWithSession` and `FindUserByAPIToken` never call `validateUsersActive`, so a user deactivated upstream keeps full node access until their session/token naturally expires or an on-interval/rate-limited background sync happens to run.

### Finding Description
`ldapAuthenticator.FindUser` performs an explicit `validateUsersActive` check and rejects inactive users at login time: [1](#0-0) .

However, once a session or API token has been created, the per-request authorization paths do not perform this check at all:
- `AuthorizedUserWithSession` only checks the local `ldap_sessions` row's expiry (`Valid` computed from `created_at + SessionTimeout`), never re-querying LDAP for active status: [2](#0-1) .
- `FindUserByAPIToken` only checks the local `ldap_user_api_tokens` row's expiry, likewise no active-status re-validation: [3](#0-2) .

These two functions are exactly the ones invoked by the web authentication middleware on every authenticated request: [4](#0-3)  and [5](#0-4) , as well as the GraphQL session middleware: [6](#0-5) .

The only mechanism that would purge/expire access for a now-inactive user is `LDAPServerStateSyncer.Work`, which deletes sessions/tokens belonging to users no longer present in `upstreamUserStateMap` after calling `validateUsersActive`: [7](#0-6) . But this sync only runs either once at startup (`UpstreamSyncInterval` default `'0s'` disables the periodic goroutine) or on a background timer gated further by `UpstreamSyncRateLimit` (default `2m0s`): [8](#0-7) . It is not invoked synchronously as part of `AuthorizedUserWithSession` or `FindUserByAPIToken`, contradicting the package-level doc comment claiming sync "happens for every auth endpoint hit": [9](#0-8) .

Consequently, exactly like the suspended `partyB` in the audit report retaining privileged capability because the relevant action path lacks the suspension check that exists elsewhere, a deactivated LDAP user here retains full authenticated node access (any role, including Admin) for up to `SessionTimeout` (default 15m) via cookie session, or up to `UserAPITokenDuration` (default 240h ≈ 10 days) via API token, unless the background syncer happens to run and purge them first.

### Impact Explanation
An operator who is deactivated/removed from LDAP (e.g., offboarded employee, compromised credential revoked upstream) can continue to use their existing browser session or, more severely, their long-lived API token (default validity up to 10 days) to fully interact with the Chainlink node's admin API — creating jobs, managing bridges, external initiators, transfers, chain/node configuration, etc., depending on their cached role — with no re-validation against the identity provider. This directly undermines the security assumption that revoking access upstream immediately revokes node access, which is the entire purpose of using LDAP as an authoritative identity source.

### Likelihood Explanation
Likelihood is high in any real deployment using LDAP authentication with `UpstreamSyncInterval` at its documented default (`'0s'`, disabling periodic re-sync) — the default configuration itself creates this window. Even with periodic sync enabled, the `UpstreamSyncRateLimit` (default 2 minutes) and the fact that sync is not triggered on the authorization hot path mean a deactivated user's still-valid session/API token remains usable in the interim, and no additional attacker action is required — it's an authorization-persistence issue purely from configuration/timing.

### Recommendation
Perform (or at minimum periodically enforce) an active-status check in `AuthorizedUserWithSession` and `FindUserByAPIToken`, or ensure the sync `Work()` reaper truly runs on every authenticated request (as the doc comment claims) rather than only on a background interval/rate limiter. At minimum, document/require `UpstreamSyncInterval` to be non-zero in production and reduce `UpstreamSyncRateLimit`, or add a lightweight synchronous LDAP active check with caching before trusting cached session/token role data.

### Proof of Concept
1. Configure node with `AuthenticationMethod = 'ldap'`, `UpstreamSyncInterval = '0s'` (the documented default) and `UserApiTokenEnabled = true`.
2. User logs in successfully while active in LDAP; `CreateSession` stores a row in `ldap_sessions`, and/or the user issues an API token via `/v2/user/token`, stored in `ldap_user_api_tokens` (`SetAuthToken`): [10](#0-9) .
3. Administrator deactivates/removes the user in the upstream LDAP directory.
4. Because `UpstreamSyncInterval` is `0s`, no periodic `Work()` call purges the stale session/token.
5. The deactivated user continues issuing authenticated requests using their existing session cookie or API key/secret; `AuthenticateBySession`/`AuthenticateByToken` succeed since `AuthorizedUserWithSession`/`FindUserByAPIToken` only check expiry, not LDAP active status, granting continued access to all endpoints matching their cached role.

### Citations

**File:** core/sessions/ldapauth/ldap.go (L12-17)
```go
User session and roles are cached and revalidated with the upstream service at the interval defined in
the local LDAP config through the Application.sessionReaper implementation in reaper.go.

Changes to the upstream identity server will propagate through and update local tables (web sessions, API tokens)
by either removing the entries or updating the roles. This sync happens for every auth endpoint hit, and
via the defined sync interval. One goroutine is created to coordinate the sync timing in the New function
```

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

**File:** core/sessions/ldapauth/ldap.go (L544-591)
```go
// SetAuthToken updates the user to use the given Authentication Token.
func (l *ldapAuthenticator) SetAuthToken(ctx context.Context, user *sessions.User, token *auth.Token) error {
	if !l.config.UserApiTokenEnabled() {
		return errors.New("API token is not enabled ")
	}

	salt := utils.NewSecret(utils.DefaultSecretSize)
	hashedSecret, err := auth.HashedSecret(token, salt)
	if err != nil {
		return fmt.Errorf("LDAPAuth SetAuthToken hashed secret error: %w", err)
	}

	err = sqlutil.TransactDataSource(ctx, l.ds, nil, func(tx sqlutil.DataSource) error {
		// Is this user a local CLI Admin or upstream LDAP user?
		// Check presence in local users table. Set localauth_user column true if present.
		// This flag omits the session/token from being purged by the sync daemon/reaper.go
		isLocalCLIAdmin := false
		err = l.ds.QueryRowxContext(ctx, "SELECT EXISTS (SELECT 1 FROM users WHERE email = $1)", user.Email).Scan(&isLocalCLIAdmin)
		if err != nil {
			return fmt.Errorf("error checking user presence in users table: %w", err)
		}

		// Remove any existing API tokens
		if _, err = l.ds.ExecContext(ctx, "DELETE FROM ldap_user_api_tokens WHERE user_email = $1", user.Email); err != nil {
			return fmt.Errorf("error executing DELETE FROM ldap_user_api_tokens: %w", err)
		}
		// Create new API token for user
		_, err = l.ds.ExecContext(
			ctx,
			"INSERT INTO ldap_user_api_tokens (user_email, user_role, localauth_user, token_key, token_salt, token_hashed_secret, created_at) VALUES ($1, $2, $3, $4, $5, $6, now())",
			user.Email,
			user.Role,
			isLocalCLIAdmin,
			token.AccessKey,
			salt,
			hashedSecret,
		)
		if err != nil {
			return fmt.Errorf("failed insert into ldap_user_api_tokens: %w", err)
		}
		return nil
	})
	if err != nil {
		return errors.New("error creating API token")
	}

	l.auditLogger.Audit(audit.APITokenCreated, map[string]any{"user": user.Email})
	return nil
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

**File:** core/sessions/ldapauth/sync.go (L56-114)
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
```

**File:** core/sessions/ldapauth/sync.go (L174-243)
```go
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

	// upstreamUserStateMap is now the most up to date source of truth
	// Now sync database sessions and roles with new data
	err = sqlutil.TransactDataSource(ctx, l.ds, nil, func(tx sqlutil.DataSource) error {
		// First, purge users present in the local ldap_sessions table but not in the upstream server
		type LDAPSession struct {
			UserEmail string
			UserRole  sessions.UserRole
		}
		var existingSessions []LDAPSession
		if err = tx.SelectContext(ctx, &existingSessions, "SELECT user_email, user_role FROM ldap_sessions WHERE localauth_user = false"); err != nil {
			return fmt.Errorf("unable to query ldap_sessions table: %w", err)
		}
		var existingAPITokens []LDAPSession
		if err = tx.SelectContext(ctx, &existingAPITokens, "SELECT user_email, user_role FROM ldap_user_api_tokens WHERE localauth_user = false"); err != nil {
			return fmt.Errorf("unable to query ldap_user_api_tokens table: %w", err)
		}

		// Create existing sessions and API tokens lookup map for later
		existingSessionsMap := make(map[string]LDAPSession)
		for _, sess := range existingSessions {
			existingSessionsMap[sess.UserEmail] = sess
		}
		existingAPITokensMap := make(map[string]LDAPSession)
		for _, sess := range existingAPITokens {
			existingAPITokensMap[sess.UserEmail] = sess
		}

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
