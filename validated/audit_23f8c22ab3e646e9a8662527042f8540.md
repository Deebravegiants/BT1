Audit Report

## Title
Disabled/deactivated LDAP users retain valid sessions and API tokens until natural expiry - ([File: core/sessions/ldapauth/ldap.go])

## Summary
The LDAP authenticator's per-request authentication paths (`AuthorizedUserWithSession` and `FindUserByAPIToken`) validate only local session/token expiry and never re-check the upstream LDAP "active" attribute. Combined with the documented default `UpstreamSyncInterval = '0s'`, which disables the periodic background revalidation job and causes it to run only once at node startup, a user disabled/removed from the LDAP directory after obtaining a session or API token retains full access for the remainder of the credential's TTL (up to `SessionTimeout`, default 15m, or `UserAPITokenDuration`, default 240h).

## Finding Description
`AuthorizedUserWithSession`, invoked on every session-cookie request via `AuthenticateBySession`, queries only the local `ldap_sessions` table for `created_at + SessionTimeout >= now()` and never calls `validateUsersActive`: [1](#0-0) . Similarly `FindUserByAPIToken`, invoked on every API-token request via `AuthenticateByToken`, checks only local `ldap_user_api_tokens` expiry: [2](#0-1) . Both feed directly into the request-level auth middleware: [3](#0-2) .

The only code path performing the upstream active-status check (`validateUsersActive`) is `FindUser` (login-time only) and the background `LDAPServerStateSyncer.Work`: [4](#0-3)  and [5](#0-4) . `LDAPServerStateSyncer.Start` only launches the recurring ticker goroutine if `UpstreamSyncInterval` is non-zero; otherwise it runs `Work` exactly once at startup: [6](#0-5) . The documented default value for this setting is `'0s'`, explicitly described as disabling the interval-based sync: [7](#0-6) . This directly contradicts the package's doc comment, which claims the sync "happens for every auth endpoint hit": [8](#0-7) .

## Impact Explanation
This is an authentication/authorization-revocation failure: a previously-legitimate but now-disabled identity (potentially holding `UserRoleAdmin` or `UserRoleEdit`) can continue to authenticate and act on the node — creating jobs, altering configuration, managing keys, or triggering bridge/job operations — for up to 10 days after being deactivated in the identity directory, using only credentials obtained prior to revocation. This maps to the in-scope "node API authentication or role bypass" impact class, since access control assumptions (that a disabled account cannot act) are violated by default configuration.

## Likelihood Explanation
No additional privilege beyond a previously-obtained, still-unexpired session cookie or API token is required by the acting party; the vulnerable state is reached purely through the shipped default (`UpstreamSyncInterval = '0s'`), not a misconfiguration deviating from defaults. The scenario (disable account after credential issuance, continue using credential) is realistic in operational settings (e.g., offboarding), and is fully reproducible via normal HTTP requests without host/database access.

## Recommendation
Perform an upstream active-status check (or a lightweight cached check with a short TTL) inside `AuthorizedUserWithSession` and `FindUserByAPIToken`, rather than relying solely on a background sync that is disabled by default. Alternatively, make `UpstreamSyncInterval` mandatory and default to a short, non-zero interval, and correct the package documentation to accurately describe when revalidation occurs.

## Proof of Concept
1. Configure `WebServer.AuthenticationMethod = 'ldap'` with `WebServer.LDAP.ActiveAttribute` set, leaving `UpstreamSyncInterval` at its default `'0s'`.
2. Log in via `POST /sessions` as an active LDAP user to obtain a session cookie, or call the API-token creation endpoint to obtain an API key/secret.
3. Have the LDAP administrator mark the account inactive in the upstream directory.
4. Continue issuing authenticated requests with the previously obtained cookie or token; `AuthorizedUserWithSession`/`FindUserByAPIToken` succeed because they only check `created_at + duration >= now()` against local Postgres tables (`core/sessions/ldapauth/ldap.go` lines 217-221 and 355-358), not upstream active state, until natural expiry or node restart.

### Citations

**File:** core/sessions/ldapauth/ldap.go (L12-17)
```go
User session and roles are cached and revalidated with the upstream service at the interval defined in
the local LDAP config through the Application.sessionReaper implementation in reaper.go.

Changes to the upstream identity server will propagate through and update local tables (web sessions, API tokens)
by either removing the entries or updating the roles. This sync happens for every auth endpoint hit, and
via the defined sync interval. One goroutine is created to coordinate the sync timing in the New function
```

**File:** core/sessions/ldapauth/ldap.go (L130-142)
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

**File:** core/sessions/ldapauth/ldap.go (L204-229)
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
```

**File:** core/sessions/ldapauth/ldap.go (L342-361)
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
```

**File:** core/web/auth/auth.go (L55-99)
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

var _ authMethod = AuthenticateBySession

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

**File:** core/sessions/ldapauth/sync.go (L163-180)
```go
	// Dedupe preserving order of highest role (sorted)
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
```

**File:** core/config/docs/core.toml (L267-269)
```text
UserAPITokenDuration = '240h0m0s' # Default
# UpstreamSyncInterval is the interval at which the background LDAP sync task will be called. A '0s' value disables the background sync being run on an interval. This check is already performed during login/logout actions, all sessions and API tokens stored in the local ldap tables are updated to match the remote server
UpstreamSyncInterval = '0s' # Default
```
