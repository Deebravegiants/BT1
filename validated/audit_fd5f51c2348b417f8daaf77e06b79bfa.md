### Title
Stale API token/session validity window recomputed from live config instead of the value in effect at issuance - ([File: core/sessions/ldapauth/ldap.go], [File: core/sessions/oidcauth/oidc.go], [File: core/sessions/localauth/orm.go])

### Summary
The Kleidi finding is a class of bug where an expiry/validity check is re-evaluated using a *currently configured* duration value instead of the duration value that was actually in effect when the timed object (the timelock proposal / here, a session or API token) was created. In `chainlink`, the LDAP and OIDC authentication providers compute API-token and session validity the same way: by adding the *live* configured duration (`UserAPITokenDuration()` / `SessionTimeout()`) to a stored `created_at`/`last_used` timestamp at query time, rather than persisting or comparing against the duration that was configured at creation time.

### Finding Description
`ldapAuthenticator.FindUserByAPIToken` and `oidcAuthenticator.FindUserByAPIToken` validate a bearer API token entirely inside a SQL predicate that references the *current* config value: [1](#0-0) [2](#0-1) 

Both queries are of the form:
```sql
SELECT ..., created_at + $2 >= now() as valid FROM ..._user_api_tokens WHERE token_key = $1
```
where `$2` is `l.config.UserAPITokenDuration().Duration()` / `oi.config.UserAPITokenDuration().Duration()` — read fresh from the live `WebServer.LDAP.UserAPITokenDuration` / `WebServer.OIDC.UserAPITokenDuration` config **at request time**, not the duration that was configured when the token row was inserted. The same pattern is used for local/LDAP/OIDC session expiry via the reapers and `findValidSession`: [3](#0-2) 

This is authenticated purely on the header-supplied token (`AuthenticateByToken` in `core/web/auth/auth.go`, reachable by any unprivileged client presenting `X-API-KEY`/`X-API-SECRET`): [4](#0-3) 

Consequence, directly analogous to the Kleidi `_afterCall`/`isOperationReady` bug (which re-checked `timestamp[id] + expirationPeriod` using the *new* `expirationPeriod` instead of the one in force when the operation was scheduled):
- If an operator **increases** `UserAPITokenDuration` (e.g. from a short value back up to a longer default, or during a config rollback), every previously-issued token whose `created_at + newDuration >= now()` suddenly becomes valid again — including tokens that had already legitimately expired under the old, shorter duration and that a client/attacker may have retained. The stale-but-retained credential is silently reactivated without any re-authentication.
- Conversely, if an operator **decreases** the duration (e.g. as a security hardening step), all outstanding tokens issued under the old, longer duration are immediately invalidated system-wide, even ones that were still well within their originally granted validity window — an availability regression exactly mirroring the Kleidi "cannot reduce the period without breaking already-scheduled operations" symptom.

### Impact Explanation
This directly affects authentication/session validity for a widely used, unprivileged-reachable surface (any HTTP client authenticating with `X-Chainlink-EA-AccessKey`/API token headers). The security-relevant direction is the reactivation case: a token that was correctly expired and should require re-authentication becomes valid again purely because of a later, unrelated config change, without the token holder proving anything new. This can effectively resurrect a leaked/rotated-out credential. Severity is Medium: it requires a specific operator config change sequence to trigger, matching the assessed "Medium" severity/"Other" type of the original Kleidi finding (unintended validity/permission state caused by comparing against a live-but-wrong parameter).

### Likelihood Explanation
Likelihood is moderate: it requires an operator to change `UserAPITokenDuration` (or `SessionTimeout`) at least once after tokens/sessions already exist — a plausible, ordinary operational action (e.g., temporarily shortening then restoring the duration, or adjusting node hardening settings) rather than an attack precondition. No attacker action beyond retaining an old, previously-issued token is required to benefit from the reactivation case.

### Recommendation
Persist the validity duration (or an explicit `expires_at` timestamp computed at issuance time) alongside `created_at` when the token/session row is created, and compare against that stored value rather than re-deriving expiry from the currently configured duration at query time. This mirrors the Kleidi fix recommendation of removing the redundant re-check against a mutable parameter and instead validating against the value that was fixed at creation/schedule time.

### Proof of Concept
1. Set `UserAPITokenDuration = "1h"`. Issue an API token; note `created_at`.
2. Wait > 1h (or manipulate `created_at` in tests, as done in `TestORM_FindUserByAPIToken_Expired`, see [5](#0-4) ) so the token is now expired under the 1h window.
3. Operator changes `UserAPITokenDuration = "240h"` (restoring default) and restarts/reloads config.
4. Re-authenticate with the same old token via `X-API-KEY`/`X-API-SECRET` through `AuthenticateByToken` → `FindUserByAPIToken`: the query `created_at + 240h >= now()` now evaluates true, and the previously-expired token is accepted again, granting the caller the associated user's role without any new credential proof.

### Citations

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

**File:** core/sessions/oidcauth/oidc.go (L297-327)
```go
// FindUserByAPIToken retrieves a possible stored user and role from the oidc_user_api_tokens table store
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
		foundUser = clsessions.User{
			Email: foundUserToken.UserEmail,
			Role:  foundUserToken.UserRole,
		}
		return nil
	})
```

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

**File:** core/web/auth/auth.go (L78-112)
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

**File:** core/sessions/oidcauth/oidc_test.go (L85-100)
```go
func TestORM_FindUserByAPIToken_Expired(t *testing.T) {
	ctx := t.Context()
	// Init OIDC authenticator
	cfg := oidcauth.TestConfig{}
	db, oidcAuthProvider := setupAuthenticationProvider(t)

	testEmail := "test@test.com"
	apiToken := "example"
	expiredTime := time.Now().Add(-cfg.UserAPITokenDuration().Duration() - time.Second)
	_, err := db.Exec("INSERT INTO oidc_user_api_tokens values ($1, 'edit', $2, '', '', $3)", testEmail, apiToken, expiredTime)
	require.NoError(t, err, "failed to insert expired token")

	// Token found but expired. expect error
	_, err = oidcAuthProvider.FindUserByAPIToken(ctx, apiToken)
	require.ErrorIs(t, err, sessions.ErrUserSessionExpired, "expected expired token to return ErrUserSessionExpired")
}
```
