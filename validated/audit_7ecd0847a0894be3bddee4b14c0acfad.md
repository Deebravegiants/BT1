This confirms the claim. The auth middleware (`AuthenticateBySession`, `AuthenticateByToken`) only calls `AuthorizedUserWithSession` / `FindUserByAPIToken`, which perform purely local time-based expiry checks against cached DB rows, with no per-request call to `WakeSessionReaper` or upstream LDAP revalidation — that only happens at login (`SessionsController.Create`) or on the background `LDAPServerStateSyncer.Work` ticker.

Audit Report

## Title
Improper Authorization — LDAP-backed sessions and API tokens remain valid after upstream account deactivation until the next sync interval - ([File: core/sessions/ldapauth/ldap.go])

## Summary
The LDAP authentication provider caches a user's role and validity locally in the `ldap_sessions` and `ldap_user_api_tokens` tables at login time. `AuthorizedUserWithSession` and `FindUserByAPIToken`, which back the gin auth middleware `AuthenticateBySession`/`AuthenticateByToken`, only check a local time-based expiry column against cached data and never re-query the upstream LDAP server for current account status per request, contradicting the package's documented behavior.

## Finding Description
The package doc comment claims upstream sync "happens for every auth endpoint hit, and via the defined sync interval" [1](#0-0) , but `AuthorizedUserWithSession` only performs `SELECT ... created_at + $2 >= now() as valid FROM ldap_sessions WHERE id = $1`, a purely local, time-bound check with no upstream call [2](#0-1) . Likewise, `FindUserByAPIToken` only checks `created_at + $2 >= now()` against the cached `ldap_user_api_tokens` row [3](#0-2) .

The gin auth middleware `AuthenticateBySession` and `AuthenticateByToken` call exactly these two functions and nothing else on the request path [4](#0-3) . The actual upstream revalidation — via `validateUsersActive` against the LDAP `ActiveAttribute` and group membership — only occurs inside `LDAPServerStateSyncer.Work`, which is invoked either by a background ticker on `UpstreamSyncInterval` or once at startup if that interval is unset (`IsInstant()`) [5](#0-4) . `WakeSessionReaper` (which nudges the reaper/sync loop) is only called from `SessionsController.Create`, i.e., at login, not on every authenticated request [6](#0-5) .

This means the security assumption implied by the doc comment ("sync happens for every auth endpoint hit") is false in the implementation, and there is no per-request mechanism that would catch an upstream deactivation between sync intervals.

## Impact Explanation
This maps to a genuine node API authorization-bypass concern: an operator disabling or removing a compromised/terminated user's LDAP account expects immediate loss of access, but the user's already-issued session cookie or API token continues to authorize requests — including admin-level actions if their cached role was Admin — until the next background sync tick, which is bounded by operator-configured `UpstreamSyncInterval` and `UpstreamSyncRateLimit`. This is a legitimate, in-scope authorization/session-revocation weakness rather than a purely theoretical issue, since the code path and doc/implementation mismatch are directly verifiable in the shipped code.

## Likelihood Explanation
The scenario requires LDAP authentication to be configured (an in-scope, supported auth mode) with a non-trivial `UpstreamSyncInterval`, plus an account deactivation event happening after a session/token was already issued — a realistic and common administrative scenario (offboarding, incident response, credential rotation). No additional privilege is needed beyond already holding a previously-valid session/token, and the window of exposure is deterministic and bounded only by the sync/rate-limit configuration, which defaults are operator controlled but the exposure mechanism itself is a code defect, not a misconfiguration by the reporting party.

## Recommendation
- Re-validate the user's "active" status (and ideally role/group membership) against the upstream LDAP server on each `AuthorizedUserWithSession`/`FindUserByAPIToken` call when `ActiveAttribute` is configured, or enforce a bounded, short mandatory re-check interval independent of the admin-configured `UpstreamSyncInterval`.
- Alternatively, cap session/token lifetime to a short, non-configurable maximum so the worst-case exposure window after upstream deactivation stays small regardless of sync settings.
- Correct the doc comment to reflect actual behavior, or better, implement per-request revalidation as originally documented.

## Proof of Concept
1. Configure LDAP auth with `UpstreamSyncInterval` set to a long duration (e.g., 24h) and `ActiveAttribute` configured.
2. A user logs in via `SessionsController.Create` → `CreateSession`, receiving a session cookie; a row is inserted into `ldap_sessions` with the cached role [6](#0-5) .
3. An administrator disables the user's account upstream in LDAP or removes them from all role groups.
4. Before the next `LDAPServerStateSyncer.Work` tick, the user continues making authenticated requests with the existing session cookie.
5. `AuthenticateBySession` → `AuthorizedUserWithSession` evaluates only `created_at + SessionTimeout >= now()` against the local `ldap_sessions` table, returns the stale cached role, and the request is authorized despite the upstream deactivation [2](#0-1) .

### Citations

**File:** core/sessions/ldapauth/ldap.go (L15-17)
```go
Changes to the upstream identity server will propagate through and update local tables (web sessions, API tokens)
by either removing the entries or updating the roles. This sync happens for every auth endpoint hit, and
via the defined sync interval. One goroutine is created to coordinate the sync timing in the New function
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

**File:** core/sessions/ldapauth/ldap.go (L345-368)
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
```

**File:** core/web/auth/auth.go (L55-112)
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

**File:** core/sessions/ldapauth/sync.go (L56-91)
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
```

**File:** core/web/sessions_controller.go (L29-31)
```go
func (sc *SessionsController) Create(c *gin.Context) {
	defer sc.App.WakeSessionReaper()
	ctx := c.Request.Context()
```
