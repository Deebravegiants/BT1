Confirmed: the code exactly matches the claim — `AuthenticateBySession` calls only `AuthorizedUserWithSession` [1](#0-0)  and `AuthenticateByToken` calls only `FindUserByAPIToken` [2](#0-1) , both of which purely read cached role data from `ldap_sessions`/`ldap_user_api_tokens` without any upstream LDAP revalidation call [3](#0-2) [4](#0-3) . The only code that reconciles roles against the upstream LDAP directory is `LDAPServerStateSyncer.Work`, invoked exclusively via a background ticker (`run()`) or once at startup — never from the request path [5](#0-4) . The package doc comment's claim that "this sync happens for every auth endpoint hit" is thus contradicted by the actual code [6](#0-5) .

Audit Report

## Title
Stale cached LDAP role/session state is used for authorization decisions without triggering upstream revalidation, contrary to documented behavior - (core/sessions/ldapauth/ldap.go)

## Summary
`AuthenticateBySession` and `AuthenticateByToken` in `core/web/auth/auth.go`, which gate every LDAP-authenticated HTTP/GraphQL request, call `AuthorizedUserWithSession` and `FindUserByAPIToken` respectively, both of which return a user's role purely from local cache tables (`ldap_sessions`, `ldap_user_api_tokens`) and never trigger or await upstream LDAP revalidation. The only revalidation mechanism, `LDAPServerStateSyncer.Work`, runs solely on a background ticker or once at startup, contradicting the package doc's claim that sync "happens for every auth endpoint hit."

## Finding Description
The `ldapauth` package doc states that role sync happens "for every auth endpoint hit, and via the defined sync interval," but the actual authentication code path never invokes any revalidation logic per request. `AuthorizedUserWithSession` selects `user_email, user_role` directly from `ldap_sessions` by session ID and returns it as-is if not expired, with an explicit comment noting "no further upstream LDAP query is performed." `FindUserByAPIToken` behaves identically against `ldap_user_api_tokens`. The reconciliation logic that actually re-queries LDAP groups and downgrades/purges stale roles lives entirely in `LDAPServerStateSyncer.Work`, called only from `run()` on a `time.NewTicker(UpstreamSyncInterval)` loop, or once at `Start` if the interval is unset. There is no call from `AuthenticateBySession`/`AuthenticateByToken` (or their downstream `Authorized*`/`FindUserBy*` calls) into `Work` or any synchronous LDAP check.

## Impact Explanation
If an operator revokes or downgrades a user's LDAP group membership after the user has an active session or API token, the stale, higher-privileged role continues to authorize requests until the next scheduled `UpstreamSyncInterval` tick. Because `AuthorizedUserWithSession`/`FindUserByAPIToken` are the sole authorization gates feeding `RequiresAdminRole`/`RequiresEditRole`/`RequiresRunRole`, this is a genuine authorization-bypass / stale-privilege window whose duration is governed by the configured (and possibly large) `UpstreamSyncInterval`.

## Likelihood Explanation
This requires only that an attacker/former-employee already hold a valid session cookie or API token at the moment their upstream LDAP privileges are revoked — a realistic operational scenario. The behavior is deterministic given the code structure: no per-request revalidation path exists, so the stale role is guaranteed to be honored until the background ticker fires.

## Recommendation
Either correct the documentation to state that revalidation is periodic-only (not per-request) and recommend a conservative default `UpstreamSyncInterval`, or modify `AuthorizedUserWithSession`/`FindUserByAPIToken` to trigger a synchronous/rate-limited revalidation against the upstream LDAP directory before returning a role used for authorization, matching the documented behavior.

## Proof of Concept
1. Configure LDAP driver with `UpstreamSyncInterval` set large (e.g., 24h).
2. User logs in while an Admin group member; `CreateSession` stores `user_role = admin` in `ldap_sessions`.
3. Operator removes the user from the Admin group upstream.
4. Before the next `LDAPServerStateSyncer.Work` tick, the user continues issuing admin-role requests using the existing session cookie; `AuthenticateBySession` → `AuthorizedUserWithSession` returns the stale cached `admin` role, and requests to admin-only endpoints (e.g., protected by `RequiresAdminRole`) succeed despite upstream revocation. This can be demonstrated as a Go integration test around `core/web/auth/auth_test.go` mocking a `ldapAuthenticator` whose `ds` cache still reflects `admin` while a fake upstream client returns a downgraded role, verifying `AuthenticateBySession` does not reflect the change until `Work` is manually invoked.

### Citations

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

**File:** core/sessions/ldapauth/ldap.go (L12-19)
```go
User session and roles are cached and revalidated with the upstream service at the interval defined in
the local LDAP config through the Application.sessionReaper implementation in reaper.go.

Changes to the upstream identity server will propagate through and update local tables (web sessions, API tokens)
by either removing the entries or updating the roles. This sync happens for every auth endpoint hit, and
via the defined sync interval. One goroutine is created to coordinate the sync timing in the New function

This implementation is read only; user mutation actions such as Delete are not supported.
```

**File:** core/sessions/ldapauth/ldap.go (L204-230)
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
```

**File:** core/sessions/ldapauth/ldap.go (L345-367)
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
