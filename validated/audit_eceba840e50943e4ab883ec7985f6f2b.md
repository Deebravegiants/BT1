This confirms the analog: `FindUserByAPIToken` in `core/sessions/ldapauth/ldap.go` only checks token expiration (`Valid` field based on `created_at + duration >= now()`), unlike `FindUser` which explicitly calls `l.validateUsersActive` before returning a user. The `Work` sync function that would purge tokens for deactivated upstream LDAP users only runs on the `UpstreamSyncInterval` timer (default `'0s'`, disabling periodic sync) and once at startup, not on every API-token-authenticated request.

### Title
Suspended/deactivated LDAP users can continue authenticating and acting via API tokens - (File: `core/sessions/ldapauth/ldap.go`)

### Summary
The Sherlock report describes suspended users retaining protocol access because a "suspended" state is checked only in some code paths and not others. The equivalent bug class exists in chainlink's LDAP authentication provider: a user deactivated in the upstream directory (`ActiveAttribute`) is blocked from establishing new sessions and is removed from listings, but an already-issued API token for that user continues to authenticate successfully because the active-status re-validation logic is not part of the API-token authentication path.

### Finding Description
`FindUser` in [1](#0-0)  explicitly calls `l.validateUsersActive([]string{email})` and rejects the user with `"user not active"` if the upstream LDAP `ActiveAttribute` marks them inactive.

In contrast, `FindUserByAPIToken`, which is invoked by `AuthenticateByToken` for every API-token-authenticated request ( [2](#0-1) ), only checks token existence and expiration against `ldap_user_api_tokens`, with no call to `validateUsersActive` or any check of the user's current upstream active state: [3](#0-2) .

The only mechanism that would purge a deactivated user's stale API token is the `LDAPServerStateSyncer.Work` function, which deletes `ldap_sessions`/`ldap_user_api_tokens` rows for users no longer present in the upstream group membership map ( [4](#0-3) ). However, `Work` is only triggered once at node startup, or periodically via `UpstreamSyncInterval` — which is disabled by default (`'0s'`) per the config comment and default value ( [5](#0-4) ) and `Start` implementation ( [6](#0-5) ). It is not triggered by each API-token-authenticated request.

Additionally, even when the sync purges the token by checking group membership presence, note that `validateUsersActive` is called separately within `Work` on the deduped upstream group members ( [7](#0-6) ) — but again this is gated entirely by the sync cadence, not per-request.

### Impact Explanation
A user removed/deactivated (e.g. offboarded employee) in the upstream LDAP/identity system, but who previously created an API token via `CreateAndSetAuthToken`/session flow, retains full API access at their previously assigned role (Admin/Edit/Run/View) until the next `UpstreamSyncInterval` cycle runs — which by default never runs automatically after startup. This allows a suspended/deactivated operator-console user to continue creating jobs, managing bridges, or performing any role-gated action via the HTTP API, defeating the intent of LDAP-driven deactivation.

### Likelihood Explanation
Requires: (1) LDAP `ActiveAttribute` deactivation configured and used to suspend a user, (2) the user had previously obtained a long-lived API token (`UserAPITokenDuration`, default 240h), and (3) `UpstreamSyncInterval` left at its default disabled value or set to a long interval. Given the default config disables periodic sync, this is a realistic operational gap for any deployment using LDAP auth with API tokens without explicitly enabling `UpstreamSyncInterval`.

### Recommendation
Call `validateUsersActive` (or an equivalent lightweight active-status check) inside `FindUserByAPIToken` before returning a valid user, mirroring the check already performed in `FindUser`. Alternatively, document and/or enforce a non-zero `UpstreamSyncInterval` when LDAP auth with API tokens is enabled, or trigger a per-request/periodic revalidation independent of the configured sync interval.

### Proof of Concept
1. Configure LDAP auth (`AuthenticationMethod = "ldap"`) with `ActiveAttribute`/`ActiveAttributeAllowedValue` set, and `UserApiTokenEnabled = true`, leaving `UpstreamSyncInterval` at default (`'0s'`).
2. As a legitimate LDAP-group user, log in and call `CreateAndSetAuthToken` to obtain an API token (`AccessKey`/`Secret`).
3. In the upstream LDAP directory, deactivate the user (set `ActiveAttribute` to a non-allowed value) or remove them from all role groups — simulating "suspension."
4. Without the node restarting or an admin manually re-triggering sync, issue an authenticated API request using the previously obtained API token header (`X-Chainlink-EA-AccessKey`/`X-Chainlink-EA-Secret`).
5. Observe that `AuthenticateByToken` → `FindUserByAPIToken` returns the user successfully (token not expired), granting the suspended user's original role-based access, since no active-status check is performed on this path.

### Citations

**File:** core/sessions/ldapauth/ldap.go (L115-142)
```go
func (l *ldapAuthenticator) FindUser(ctx context.Context, email string) (sessions.User, error) {
	email = strings.ToLower(email)

	// First check for the supported local admin users table
	var foundLocalAdminUser sessions.User
	checkErr := l.ds.GetContext(ctx, &foundLocalAdminUser, "SELECT * FROM users WHERE lower(email) = lower($1)", email)
	if checkErr == nil {
		return foundLocalAdminUser, nil
	}
	// If error is not nil, there was either an issue or no local users found
	if !errors.Is(checkErr, sql.ErrNoRows) {
		// If the error is not that no local user was found, log and exit
		l.lggr.Errorf("error searching users table: %v", checkErr)
		return sessions.User{}, errors.New("error Finding user")
	}

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

**File:** core/sessions/ldapauth/ldap.go (L205-230)
```go
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
```

**File:** core/web/auth/auth.go (L78-99)
```go
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

**File:** core/sessions/ldapauth/sync.go (L174-185)
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

**File:** core/config/docs/core.toml (L268-271)
```text
# UpstreamSyncInterval is the interval at which the background LDAP sync task will be called. A '0s' value disables the background sync being run on an interval. This check is already performed during login/logout actions, all sessions and API tokens stored in the local ldap tables are updated to match the remote server
UpstreamSyncInterval = '0s' # Default
# UpstreamSyncRateLimit defines a duration to limit the number of query/API calls to the upstream LDAP provider. It prevents the sync functionality from being called multiple times within the defined duration
UpstreamSyncRateLimit = '2m0s' # Default
```
