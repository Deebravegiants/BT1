## Finding: session/API-token validity is recomputed from the live config value instead of being pinned at issuance

This is a solid structural analog to the reported bug. The loan report's root cause is that a *mutable, admin-controlled parameter* (`feePercent`) is read live and applied to *already-created* resources (active loans) instead of being snapshotted onto the resource at creation time. The same pattern exists in this repo's session/API-token expiry checks.

### Where it happens

- `core/sessions/localauth/orm.go` `findValidSession`: validity is computed as `last_used + $2 >= now()`, where `$2` is `o.sessionDuration`, the **current** `WebServer.SessionTimeout` value read at query time, not a value captured when the session was created. [1](#0-0) 

- `core/sessions/oidcauth/oidc.go` `AuthorizedUserWithSession`: validity is `created_at + $2 >= now()` where `$2 = oi.config.SessionTimeout().Duration()`, again the live config value. [2](#0-1) 

- `core/sessions/oidcauth/oidc.go` `FindUserByAPIToken` and `core/sessions/ldapauth/ldap.go` `FindUserByAPIToken`: token validity is `created_at + $2 >= now()` where `$2 = ...UserAPITokenDuration().Duration()`, the live config value. [3](#0-2) [4](#0-3) 

- `core/sessions/ldapauth/sync.go` `Work` purges stale sessions/tokens using `l.config.SessionTimeout()...` / `l.config.UserAPITokenDuration()...` computed at sync time, not at issuance. [5](#0-4) 

None of these creation records (`sessions`, `ldap_sessions`, `ldap_user_api_tokens`, `oidc_sessions`, `oidc_user_api_tokens`) store the TTL/duration that was in effect when the credential was minted — only `created_at`/`last_used`. The effective lifetime of every outstanding session/token is therefore whatever `WebServer.SessionTimeout` / `WebServer.LDAP.UserAPITokenDuration` / `WebServer.OIDC.UserAPITokenDuration` happens to be *at the moment of the check*, exactly like the fee bug where a loan's effective cost was whatever `feePercent` happened to be at repayment time rather than what was agreed at loan creation.

### Why this matters

Because the TTL is not pinned to the resource, any operator change to these settings is retroactive across every already-issued session/token, not just future ones:
- If the duration is increased for an unrelated operational reason, previously-issued (and possibly leaked, or intentionally-to-be-abandoned) tokens/sessions that should have already lapsed under the policy in force when they were issued become valid again — an unprivileged holder of an old/leaked credential regains access without re-authenticating, purely because of an admin config change elsewhere.
- There is no way to reason about, or audit, an individual session/token's real expiration, since it is defined by a global mutable setting rather than a property of the credential itself.

This satisfies the report's "unprivileged-actor analog in ... session/token handling" scope: the affected party is the holder of a pre-existing session/API token whose expected validity window is silently altered without their consent, mirroring the borrower whose loan fee changes without consent.

### Recommendation
Persist the effective expiration/duration value on the session/token row at creation time (e.g., an `expires_at` column computed once at issuance), and compare against that stored value on every subsequent check instead of re-reading the live config. Config changes should then only affect newly-issued sessions/tokens, not outstanding ones.

<br>

Note: this same live-vs-pinned-config theme repeats in adjacent code (e.g. `deleteStaleSessions`/`deleteStaleAPITokens` reapers), which reinforces that the pattern is systemic rather than a one-off oversight, but the core reachable, unprivileged-actor-affecting instances are the four cited above.

### Citations

**File:** core/sessions/localauth/orm.go (L68-75)
```go
// findValidSession finds an unexpired session by its ID and returns the associated email.
func (o *orm) findValidSession(ctx context.Context, sessionID string) (email string, err error) {
	if err := o.ds.GetContext(ctx, &email, "SELECT email FROM sessions WHERE id = $1 AND last_used + $2 >= now() FOR UPDATE", sessionID, o.sessionDuration); err != nil {
		o.lggr.Infof("query result: %v", email)
		return email, pkgerrors.Wrap(err, "no matching user for provided session token")
	}
	return email, nil
}
```

**File:** core/sessions/oidcauth/oidc.go (L298-321)
```go
func (oi *oidcAuthenticator) FindUserByAPIToken(ctx context.Context, apiToken string) (clsessions.User, error) {
	if !oi.config.UserAPITokenEnabled() {
		return clsessions.User{}, errors.New("API token is not enabled")
	}

	var foundUser clsessions.User
	err := sqlutil.TransactDataSource(ctx, oi.ds, nil, func(tx sqlutil.DataSource) error {
		// Query the oidc user API token table for given token, user role and email are cached so
		// no further upstream OIDC query is performed, sessions and tokens are synced against the upstream server
		// via the UpstreamSyncInterval config and reaper.go sync implementation
		var foundUserToken struct {
			UserEmail string
			UserRole  clsessions.UserRole
			Valid     bool
		}
		if err := tx.GetContext(ctx, &foundUserToken,
			"SELECT user_email, user_role, created_at + $2 >= now() as valid FROM oidc_user_api_tokens WHERE token_key = $1",
			apiToken, oi.config.UserAPITokenDuration().Duration(),
		); err != nil {
			return err
		}
		if !foundUserToken.Valid {
			return clsessions.ErrUserSessionExpired
		}
```

**File:** core/sessions/oidcauth/oidc.go (L356-371)
```go
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

**File:** core/sessions/ldapauth/sync.go (L93-105)
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

```
