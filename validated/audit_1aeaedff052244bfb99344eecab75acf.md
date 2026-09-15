Based on the code review, the technical claim is well-supported by the actual source.

`AuthorizedUserWithSession` and `FindUserByAPIToken` both authorize purely from local `ldap_sessions`/`ldap_user_api_tokens` rows, comparing only `created_at + duration >= now()`, with no call to the LDAP server or to `Work()`. [1](#0-0) [2](#0-1) 

`LDAPServerStateSyncer.Start` only revalidates on a periodic goroutine if `UpstreamSyncInterval` is non-zero, or once at startup if it's `0s` (`IsInstant()`), and nowhere is `Work()` invoked from the auth-check code paths. [3](#0-2) 

`CreateSession` (login) only calls `FindUser` for the logging-in user's own role and inserts a new session row — it never triggers a resync of other users' existing sessions. [4](#0-3) 

The package doc comment's claim that "This sync happens for every auth endpoint hit" is contradicted by the code, which only checks local cached data on every auth endpoint hit and never calls upstream/`Work()` per-request. [5](#0-4) 

I was unable to render `docs/CONFIG.md` content beyond a placeholder line (it's a generated file with `DO NOT EDIT` header pointing to `docs/*.toml` sources), so I could not directly confirm the exact wording "already performed during login/logout actions" is present in a currently-rendered doc, though the search index found matching text in `core/config/docs/core.toml` and `docs/CONFIG.md`. This is a minor gap but doesn't affect the core code-behavior finding, which is independently verified from source.

This matches the described bug class precisely: a cached authorization value (role/session validity) is trusted by security decision points (`AuthorizedUserWithSession`, `FindUserByAPIToken`) without forcing revalidation against the authoritative upstream source, and revalidation only happens on a timer/startup — which, under the documented `'0s'` default, means it happens exactly once at process start and never again for the life of the running node. This is a genuine, code-verifiable authorization/staleness issue reachable by any user whose session/token was valid at creation time but whose role is later revoked upstream — not requiring any special privilege beyond normal authenticated API use, and not an operator-misconfiguration-only issue since it's the documented default behavior.

Audit Report

## Title
Stale LDAP session/role cache is never revalidated against upstream server, allowing revoked/demoted users to retain elevated privileges - (File: core/sessions/ldapauth/sync.go, core/sessions/ldapauth/ldap.go)

## Summary
The `ldapauth` authentication provider caches a user's session and role locally after login, and `AuthorizedUserWithSession`/`FindUserByAPIToken` authorize every subsequent API request purely from these local cached rows, never contacting the upstream LDAP server or triggering `LDAPServerStateSyncer.Work()`. Revalidation against upstream only happens via a background timer (if `UpstreamSyncInterval` is configured non-zero) or once at process startup under the documented default `'0s'` setting, meaning a user demoted or removed upstream keeps their stale elevated role for the full `SessionTimeout`/`UserAPITokenDuration` lifetime.

## Finding Description
`AuthorizedUserWithSession` (core/sessions/ldapauth/ldap.go:345-373) and `FindUserByAPIToken` (core/sessions/ldapauth/ldap.go:204-236) both query only the local `ldap_sessions`/`ldap_user_api_tokens` tables, checking `created_at + duration >= now()` and returning the cached `UserRole` directly — no upstream LDAP query, and no call to `Work()`. The only code path that resyncs cached roles against upstream state is `LDAPServerStateSyncer.Work()`, invoked either on a fixed timer (`run()`, if `UpstreamSyncInterval` is non-zero) or exactly once at `Start()` if `UpstreamSyncInterval().IsInstant()` (the documented `0s` default) (core/sessions/ldapauth/sync.go:56-68). `CreateSession` (login) only refreshes the logging-in user's own role via `FindUser`; it does not trigger a resync of other users' existing cached sessions (core/sessions/ldapauth/ldap.go:396-456). The package doc comment's claim that sync "happens for every auth endpoint hit" is not implemented in code — no auth-check function invokes `Work()` or performs an upstream lookup.

## Impact Explanation
This is a concrete authorization/role-bypass bug: under the documented default configuration, once a session or API token is issued with an elevated role (Admin/Edit/Run), that role is trusted for the full lifetime of the session/token even if the user is demoted or removed from the corresponding upstream LDAP group in the interim. This can allow a formerly-privileged, now-revoked user to continue performing privileged operations (job creation/mutation, key management) gated by `RequiresAdminRole`/`RequiresRunRole` in `core/web/auth/auth.go`, for up to the full `SessionTimeout`/`UserAPITokenDuration` window after revocation — a legitimate node API authentication/role bypass impact class.

## Likelihood Explanation
The condition is triggered under the config default (`UpstreamSyncInterval = '0s'`), which per the LDAP sync design causes only a single startup sync and no further periodic resyncing unless an operator explicitly sets a non-zero interval. Any already-authenticated (previously privileged) user retains this stale privilege automatically — no additional attacker action or special access is required beyond normal API use with an already-issued session/token.

## Recommendation
Either invoke `LDAPServerStateSyncer.Work` (or a targeted per-user upstream lookup) inside `AuthorizedUserWithSession`/`FindUserByAPIToken` before trusting the cached role, or clearly document that revalidation only occurs on the configured `UpstreamSyncInterval` timer/startup, and require/enforce a short non-zero interval rather than allowing the `'0s'` default that produces only a one-time startup sync.

## Proof of Concept
1. Deploy a node with `ldapauth` driver and default config (`UpstreamSyncInterval = '0s'`).
2. `alice`, a member of the upstream LDAP Admin group, logs in via `CreateSession`, receiving a session cached with `UserRoleAdmin` in `ldap_sessions` (core/sessions/ldapauth/ldap.go:440-452).
3. An operator removes `alice` from the upstream Admin group without restarting the node process and without configuring a sync timer.
4. `alice` continues calling Admin-gated endpoints; `AuthorizedUserWithSession` (core/sessions/ldapauth/ldap.go:345-373) only checks the local `created_at + SessionTimeout >= now()` condition and returns the cached `UserRoleAdmin`, so `RequiresAdminRole` in `core/web/auth/auth.go` continues to authorize her requests until the session naturally expires.

### Citations

**File:** core/sessions/ldapauth/ldap.go (L12-17)
```go
User session and roles are cached and revalidated with the upstream service at the interval defined in
the local LDAP config through the Application.sessionReaper implementation in reaper.go.

Changes to the upstream identity server will propagate through and update local tables (web sessions, API tokens)
by either removing the entries or updating the roles. This sync happens for every auth endpoint hit, and
via the defined sync interval. One goroutine is created to coordinate the sync timing in the New function
```

**File:** core/sessions/ldapauth/ldap.go (L210-221)
```go
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
```

**File:** core/sessions/ldapauth/ldap.go (L349-361)
```go
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

**File:** core/sessions/ldapauth/ldap.go (L396-456)
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
