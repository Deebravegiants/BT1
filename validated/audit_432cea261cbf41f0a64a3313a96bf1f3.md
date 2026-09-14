Based on my investigation, the local `sessions` table check has a notable difference from the LDAP/OIDC equivalents that mirrors the "staleness" bug class from the report: the local ORM's session validity check does not appear to independently enforce an absolute/hard expiry the same way — but let me verify this precisely before concluding.I found a concrete analog: `core/sessions/localauth/orm.go`'s `FindUserByAPIToken` performs no staleness/freshness check on the token whatsoever, unlike every other credential path in this same codebase.

### Title
Local-auth API tokens (`token_key`) never expire or get freshness-checked, unlike sessions, LDAP, and OIDC tokens - (File: core/sessions/localauth/orm.go)

### Summary
The Sherlock report flags `Oracle.getUnderlyingPrice` for trusting a price value without checking its `latestRoundData` freshness/staleness fields, allowing stale data to be used for a security-critical decision (liquidation). The direct analog in this chainlink codebase is `orm.FindUserByAPIToken` in the local authentication provider, which accepts a `token_key` credential and grants API access without checking any "last used"/"issued at"/duration field for staleness — even though every sibling authentication mechanism in the same package/repo (local sessions, LDAP sessions, LDAP API tokens, OIDC sessions, OIDC API tokens) explicitly enforces a staleness/expiry window before trusting the credential.

### Finding Description
`FindUserByAPIToken` in `core/sessions/localauth/orm.go` is:
```go
func (o *orm) FindUserByAPIToken(ctx context.Context, apiToken string) (user sessions.User, err error) {
	sql := "SELECT * FROM users WHERE token_key = $1"
	err = o.ds.GetContext(ctx, &user, sql, apiToken)
	return
}
``` [1](#0-0) 

There is no timestamp, no duration comparison, and no `updated_at`/`created_at` freshness check applied to the token before returning the associated user — the query only checks that the `token_key` string matches. This is the "answer" equivalent of `Oracle.getUnderlyingPrice`: it accepts the value (the token) without validating that it is still "fresh"/valid over time.

Compare this to every other credential-lookup path in the exact same codebase, all of which validate a staleness/expiry window as part of the authorization decision:

- Local session lookup enforces `last_used + sessionDuration >= now()`:
```go
func (o *orm) findValidSession(ctx context.Context, sessionID string) (email string, err error) {
	if err := o.ds.GetContext(ctx, &email, "SELECT email FROM sessions WHERE id = $1 AND last_used + $2 >= now() FOR UPDATE", sessionID, o.sessionDuration); err != nil {
``` [2](#0-1) 

- LDAP API tokens explicitly check `created_at + duration >= now()` and purge if expired:
```go
err := l.ds.GetContext(ctx, &foundUserToken,
    "SELECT user_email, user_role, created_at + $2 >= now() as valid FROM ldap_user_api_tokens WHERE token_key = $1",
    apiToken, l.config.UserAPITokenDuration().Duration(),
)
``` [3](#0-2) 

- OIDC API tokens perform the identical duration check:
```go
if err := tx.GetContext(ctx, &foundUserToken,
    "SELECT user_email, user_role, created_at + $2 >= now() as valid FROM oidc_user_api_tokens WHERE token_key = $1",
    apiToken, oi.config.UserAPITokenDuration().Duration(),
); err != nil {
``` [4](#0-3) 

- Vault's JWT-based and allowlist-based auth mechanisms both enforce hard expiry checks (`claims.ExpiresAt`, `allowlistedRequest.ExpiryTimestamp`) before authorizing a request: [5](#0-4) [6](#0-5) 

The local-auth `users.token_key` API token, by contrast, once set via `SetAuthToken`, remains permanently valid with no server-side expiry mechanism, no reaper equivalent to `sessionReaper` (which only reaps the `sessions` table, not API tokens), and no config knob analogous to `UserAPITokenDuration` for the local provider: [7](#0-6) [8](#0-7) 

This lookup is reachable directly from the unprivileged/external HTTP request path via `AuthenticateByToken` in `core/web/auth/auth.go`, which is one of the pluggable `authMethod`s wired into the router for all API/CLI token-authenticated endpoints.

### Impact Explanation
Just as the Oracle bug allows a stale price to be trusted indefinitely for a liquidation decision, a local-auth API token in this codebase is trusted indefinitely with no staleness check at all — there is no expiry, no idle-timeout enforcement, and no automatic revocation analogous to `sessionReaper`/LDAP-OIDC's `UserAPITokenDuration`. If a token is leaked (e.g., via logs, CI artifacts, shared config), it remains a permanently valid credential for API/CLI access under the user's role (Admin/Edit/Run), with no time-based mitigation, unlike every parallel authentication mechanism in this same repo, which treats credential freshness as a required security control.

### Likelihood Explanation
Likelihood is moderate-to-high for a leaked or long-outstanding token scenario: this is the standard local (default) authentication method (`AuthenticationMethod = 'local'`) for the Chainlink node's HTTP API, and `token_key` generation/rotation (`SetAuthToken`) is a normal, encouraged CLI workflow (`chainlink admin login`, API token creation). Since there is no automatic expiry, any token issued once remains valid until a user proactively calls `DeleteAuthToken`/rotates it — an operational gap directly analogous to trusting a stale oracle answer indefinitely because no staleness bound was ever enforced.

### Recommendation
Add a staleness/expiry check to `FindUserByAPIToken` in `core/sessions/localauth/orm.go`, mirroring the LDAP/OIDC pattern — introduce a `UserAPITokenDuration`-equivalent config for the local provider and validate `updated_at + duration >= now()` (or a dedicated `created_at` on token issuance) before returning the user, purging on expiry the same way LDAP/OIDC purge stale tokens:
```go
func (o *orm) FindUserByAPIToken(ctx context.Context, apiToken string) (user sessions.User, err error) {
	sql := "SELECT * FROM users WHERE token_key = $1 AND updated_at + $2 >= now()"
	err = o.ds.GetContext(ctx, &user, sql, apiToken, o.apiTokenDuration)
	return
}
```
Also extend `sessionReaper`/introduce an API-token reaper to purge stale `token_key` values proactively, consistent with `deleteStaleSessions`.

### Proof of Concept
1. Create a local API token via `SetAuthToken` (e.g., through `chainlink admin login` or `POST /v2/user/token`). [9](#0-8) 
2. Use the token to authenticate via `AuthenticateByToken` on any protected `/v2/*` endpoint.
3. Wait an arbitrarily long time (weeks/months) — unlike the LDAP/OIDC equivalents, the token never becomes invalid due to age; only an explicit `DeleteAuthToken` call revokes it.
4. Compare against `TestORM_FindUserByAPIToken_Expired` for LDAP/OIDC, which demonstrates the expected expiry behavior these mechanisms have and the local provider lacks: [10](#0-9)

### Citations

**File:** core/sessions/localauth/orm.go (L48-53)
```go
// FindUserByAPIToken will attempt to return an API user via the user's table token_key column.
func (o *orm) FindUserByAPIToken(ctx context.Context, apiToken string) (user sessions.User, err error) {
	sql := "SELECT * FROM users WHERE token_key = $1"
	err = o.ds.GetContext(ctx, &user, sql, apiToken)
	return
}
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

**File:** core/sessions/localauth/orm.go (L331-340)
```go
// SetAuthToken updates the user to use the given Authentication Token.
func (o *orm) SetAuthToken(ctx context.Context, user *sessions.User, token *auth.Token) error {
	salt := utils.NewSecret(utils.DefaultSecretSize)
	hashedSecret, err := auth.HashedSecret(token, salt)
	if err != nil {
		return pkgerrors.Wrap(err, "user")
	}
	sql := "UPDATE users SET token_salt = $1, token_key = $2, token_hashed_secret = $3, updated_at = now() WHERE email = $4 RETURNING *"
	return o.ds.GetContext(ctx, user, sql, salt, token.AccessKey, hashedSecret, user.Email)
}
```

**File:** core/sessions/ldapauth/ldap.go (L218-221)
```go
	err := l.ds.GetContext(ctx, &foundUserToken,
		"SELECT user_email, user_role, created_at + $2 >= now() as valid FROM ldap_user_api_tokens WHERE token_key = $1",
		apiToken, l.config.UserAPITokenDuration().Duration(),
	)
```

**File:** core/sessions/oidcauth/oidc.go (L313-316)
```go
		if err := tx.GetContext(ctx, &foundUserToken,
			"SELECT user_email, user_role, created_at + $2 >= now() as valid FROM oidc_user_api_tokens WHERE token_key = $1",
			apiToken, oi.config.UserAPITokenDuration().Duration(),
		); err != nil {
```

**File:** core/capabilities/vault/allow_list_based_auth.go (L64-68)
```go
	if time.Now().UTC().Unix() > int64(allowlistedRequest.ExpiryTimestamp) {
		authorizedRequestStr := string(allowlistedRequest.RequestDigest[:])
		r.lggr.Debugw("AllowListBasedAuth authorization expired", "method", req.Method, "requestID", req.ID, "authorizedRequestStr", authorizedRequestStr, "expiryTimestamp", allowlistedRequest.ExpiryTimestamp)
		return nil, errors.New("request authorization expired")
	}
```

**File:** core/capabilities/vault/jwt_based_auth.go (L258-269)
```go
	token, err := jwt.Parse(tokenString, func(token *jwt.Token) (any, error) {
		if _, methodOK := token.Method.(*jwt.SigningMethodRSA); !methodOK {
			return nil, fmt.Errorf("%w: unsupported alg %v", ErrInvalidToken, token.Header["alg"])
		}
		return rsaKey, nil
	},
		jwt.WithIssuer(v.issuerURL),
		jwt.WithAudience(v.audience),
		jwt.WithExpirationRequired(),
		jwt.WithIssuedAt(),
		jwt.WithLeeway(jwtValidationLeeway),
	)
```

**File:** core/sessions/localauth/reaper.go (L44-48)
```go
// DeleteStaleSessions deletes all sessions before the passed time.
func (sr *sessionReaper) deleteStaleSessions(ctx context.Context, before time.Time) error {
	_, err := sr.ds.ExecContext(ctx, "DELETE FROM sessions WHERE last_used < $1", before)
	return err
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
