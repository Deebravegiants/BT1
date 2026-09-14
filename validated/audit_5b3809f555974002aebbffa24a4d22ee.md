Confirmed: `AuthorizedUserWithSession` reads the cached role directly from `ldap_sessions`/`ldap_user_api_tokens` [1](#0-0)  without ever re-querying LDAP, and refresh only happens via `LDAPServerStateSyncer.Work` [2](#0-1) , which per `Start` is only invoked once at boot when `UpstreamSyncInterval` is the documented default `'0s'` [3](#0-2) [4](#0-3) , and the background ticker is not started in that case.

### Title
Stale cached LDAP role/session persists indefinitely after upstream revocation when `UpstreamSyncInterval` is left at its default disabled value - (File: core/sessions/ldapauth/sync.go)

### Summary
The LDAP authentication provider caches each authenticated user's role in the local `ldap_sessions` and `ldap_user_api_tokens` tables at login time, and every subsequent request is authorized purely against that cached row with no upstream check [5](#0-4) . The only mechanism that reconciles this cache with the upstream LDAP directory is `LDAPServerStateSyncer.Work`, which removes a user's group membership and downgrades/removes their cached role [6](#0-5) . This reconciliation is only run on a recurring timer when `UpstreamSyncInterval` is configured to a non-zero value; when left at its documented default of `'0s'`, `Work` is invoked exactly once at node startup and never again for the lifetime of the process [3](#0-2) .

### Finding Description
`ldapAuthenticator.AuthorizedUserWithSession` is the function that backs the `AuthenticateBySession`/`AuthenticateGQL` middleware used on every authenticated web/GraphQL request [7](#0-6) [8](#0-7) . It resolves the caller's role solely from the `ldap_sessions` table row created at login, explicitly documented as "no further upstream LDAP query is performed" [1](#0-0) . The same pattern applies to API tokens via `FindUserByAPIToken`, which reads `ldap_user_api_tokens` and is likewise only refreshed by the sync job [9](#0-8) .

The single mechanism intended to invalidate/refresh these cached roles after an admin revokes a user's LDAP group membership is `LDAPServerStateSyncer.Work`, which re-queries the LDAP groups and issues `UPDATE ldap_sessions SET user_role = ...` / deletes sessions for users no longer present upstream [10](#0-9) . Whether this job ever runs again after node startup depends entirely on `UpstreamSyncInterval`. The package doc comment claims "This sync happens for every auth endpoint hit, and via the defined sync interval" [11](#0-10) , but that is not actually true of the code: `AuthorizedUserWithSession`, `CreateSession`, and `FindUserByAPIToken` never call `Work` or the syncer at all — they only read/write the cached tables [12](#0-11) . `Start` only launches the recurring ticker goroutine `l.run()` when `UpstreamSyncInterval().IsInstant()` is false (i.e., non-zero); otherwise it runs `Work` exactly once at startup and never schedules it again [3](#0-2) . The documented default value for `UpstreamSyncInterval` is `'0s'` [4](#0-3) , meaning any deployment left on defaults has no periodic re-sync at all.

Consequently, once a user authenticates and receives an `admin`/`edit` role cached into `ldap_sessions`, revoking that user from the corresponding LDAP group upstream has zero effect on that user's already-issued session or API token: they retain the old cached role for the full `SessionTimeout` (default `15m0s`) for web sessions, or the full `UserAPITokenDuration` (default `240h0m0s`, i.e. 10 days) for API tokens — since expiry, not revocation, is the only thing that purges these rows [13](#0-12) [14](#0-13) .

### Impact Explanation
This is the same bug class as the Budibase advisory: an operator-initiated revocation of a user's privileged role does not propagate to the cache that the authentication/authorization middleware actually trusts, so the revoked identity retains admin/edit/run access for an extended window (up to the session timeout, and up to 10 days by default for API tokens) purely due to a stale cache read path. Given `AuthorizedUserWithSession` and `FindUserByAPIToken` are the exact functions gating every authenticated Chainlink node HTTP/GraphQL request when LDAP auth is enabled, a terminated/demoted employee retains full admin control (job creation/deletion, key management, bridge configuration, etc.) on the node for the entire stale-cache window.

### Likelihood Explanation
This requires the operator to have configured `WebServer.AuthenticationMethod = 'ldap'` and to be relying on group revocation as the offboarding mechanism, which is the intended/expected LDAP admin workflow. Because `UpstreamSyncInterval = '0s'` is the documented default, any deployment that does not explicitly override this config is exposed by default — no misconfiguration by an attacker is required, only reliance on the shipped default.

### Recommendation
- Change the default guidance/behavior so that `UpstreamSyncInterval` is non-zero out of the box, or make `Start` always schedule the recurring `run()` loop regardless of the `IsInstant()` check (running once at startup should not be a substitute for periodic re-validation).
- Additionally, have `AuthorizedUserWithSession` and `FindUserByAPIToken` perform a lightweight "is this user still in an authorized group" check (or at minimum shorten effective session/token life) rather than trusting the locally cached role indefinitely between syncs.
- Update the package doc comment in `core/sessions/ldapauth/ldap.go` to accurately reflect that no per-request upstream re-validation occurs, so operators understand the real revocation-propagation delay.

### Proof of Concept
1. Configure the node with `WebServer.AuthenticationMethod = 'ldap'` and leave `WebServer.LDAP.UpstreamSyncInterval` unset (defaults to `'0s'`).
2. Add `victim@example.com` to the LDAP `NodeAdmins` group and have them log in via `POST /sessions`, which calls `ldapAuthenticator.CreateSession` and inserts a row into `ldap_sessions` with `user_role = 'admin'` [15](#0-14) .
3. As the node operator, remove `victim@example.com` from `NodeAdmins` in the upstream LDAP directory (revocation).
4. Using the still-valid session cookie, call any admin-only endpoint (e.g. `PATCH /v2/users` to change another user's role). The request succeeds because `AuthorizedUserWithSession` returns the cached `admin` role from `ldap_sessions` without contacting LDAP [16](#0-15) .
5. The revoked admin privilege remains usable until `SessionTimeout` elapses (default 15 minutes) or until an operator manually restarts the node / configures a non-zero `UpstreamSyncInterval` to trigger `Work`.

### Citations

**File:** core/sessions/ldapauth/ldap.go (L12-17)
```go
User session and roles are cached and revalidated with the upstream service at the interval defined in
the local LDAP config through the Application.sessionReaper implementation in reaper.go.

Changes to the upstream identity server will propagate through and update local tables (web sessions, API tokens)
by either removing the entries or updating the roles. This sync happens for every auth endpoint hit, and
via the defined sync interval. One goroutine is created to coordinate the sync timing in the New function
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

**File:** core/sessions/ldapauth/ldap.go (L342-372)
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
```

**File:** core/sessions/ldapauth/ldap.go (L396-457)
```go
func (l *ldapAuthenticator) CreateSession(ctx context.Context, sr sessions.SessionRequest) (string, error) {
	conn, err := l.ldapClient.CreateEphemeralConnection()
	if err != nil {
		return "", errors.New("unable to establish connection to LDAP server with provided URL and credentials")
	}
	defer conn.Close()

	var returnErr error

	// Attempt to LDAP Bind with user provided credentials
	escapedEmail := ldap.EscapeFilter(strings.ToLower(sr.Email))
	searchBaseDN := fmt.Sprintf("%s=%s,%s,%s", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())
	if err = conn.Bind(searchBaseDN, sr.Password); err != nil {
		l.lggr.Infof("Error binding user authentication request in LDAP Bind: %v", err)
		returnErr = errors.New("unable to log in with LDAP server. Check credentials")
	}

	// Bind was successful meaning user and credentials are present in LDAP directory
	// Reuse FindUser functionality to fetch user roles used to create ldap_session entry
	// with cached user email and role
	foundUser, err := l.FindUser(ctx, escapedEmail)
	if err != nil {
		l.lggr.Infof("Successful user login, but error querying for user groups: user: %s, error %v", escapedEmail, err)
		returnErr = errors.New("log in successful, but no assigned groups to assume role")
	}

	isLocalUser := false
	if returnErr != nil {
		// Unable to log in against LDAP server, attempt fallback local auth with credentials, case of local CLI Admin account
		// Successful local user sessions can not be managed by the upstream server and have expiration handled by the reaper sync module
		foundUser, returnErr = l.localLoginFallback(ctx, sr)
		isLocalUser = true
	}

	// If err is still populated, return
	if returnErr != nil {
		return "", returnErr
	}

	l.lggr.Infof("Successful LDAP login request for user %s - %s", sr.Email, foundUser.Role)

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

	l.auditLogger.Audit(audit.AuthLoginSuccessNo2FA, map[string]any{"email": sr.Email})

	return session.ID, nil
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

**File:** core/sessions/ldapauth/sync.go (L93-120)
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

	// For each defined role/group, query for the list of group members to gather the full list of possible users
	users := []sessions.User{}

```

**File:** core/sessions/ldapauth/sync.go (L180-275)
```go
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

**File:** core/web/auth/gql.go (L25-47)
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
```
