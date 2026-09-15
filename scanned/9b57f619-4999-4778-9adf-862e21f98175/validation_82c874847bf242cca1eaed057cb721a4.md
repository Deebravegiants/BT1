### Title
Cached LDAP/OIDC API tokens remain valid for authentication after upstream user deactivation/removal until the periodic sync interval elapses - (File: core/sessions/ldapauth/ldap.go, core/sessions/ldapauth/sync.go, core/sessions/oidcauth/oidc.go)

### Summary
`FindUserByAPIToken` for both the LDAP and OIDC authentication providers validates an API token purely against a locally cached row (`ldap_user_api_tokens` / `oidc_user_api_tokens`) using a time-based expiration check, without re-checking the upstream identity provider on each request. Revocation of a user's access upstream (e.g., an admin removing the user from an LDAP group or disabling the account, or de-provisioning in OIDC) is only reflected locally when the periodic `LDAPServerStateSyncer.Work` / OIDC equivalent job runs. This is directly analogous to the JOJO issue: an off-chain "cancellation" (upstream revocation) does not prevent continued "on-chain" (node API) use of a still-cryptographically-valid credential until expiration/sync catches up.

### Finding Description
`AuthenticateByToken` in `core/web/auth/auth.go` calls `authr.FindUserByAPIToken(ctx, token.AccessKey)` to authenticate a caller's node API token: [1](#0-0) 

For the LDAP provider, `FindUserByAPIToken` only checks the cached table `ldap_user_api_tokens` with a validity computed from `created_at + duration >= now()`. It never re-queries the LDAP directory to check if the user is still a member of any role group or still "active": [2](#0-1) 

The same pattern exists for OIDC's `FindUserByAPIToken`: [3](#0-2) 

The only mechanism that reconciles the local cache with the upstream source of truth (removing sessions/tokens for users no longer present/active upstream, or updating their role) is the periodic background job `LDAPServerStateSyncer.Work`, which runs on a `UpstreamSyncInterval` ticker (or once at startup if unset): [4](#0-3) [5](#0-4) 

Notably the package-level doc comment claims "This sync happens for every auth endpoint hit, and via the defined sync interval," but the actual `FindUserByAPIToken` implementation shown above performs no upstream call per request — it is purely a local time-based expiry check: [6](#0-5) 

So if an operator revokes a user's access upstream (removes them from the LDAP group / OIDC identity provider), that user's already-issued API token (analogous to the pre-signed JOJO order) continues to authenticate successfully against the node's HTTP API — with the same role/permissions cached at token-creation time — until the next scheduled `Work()` sync run deletes the stale row from `ldap_user_api_tokens`/`oidc_user_api_tokens`.

### Impact Explanation
A revoked/de-provisioned user (or an attacker who obtained/retained the token before revocation) can continue to authenticate to the node's admin API — creating jobs, managing bridges, external initiators, keys, etc., depending on the cached role — for up to the length of `UpstreamSyncInterval` after the upstream cancellation. This mirrors the JOJO bug class: cancellation of an authorization ("order"/"access") off-chain (upstream identity provider) does not prevent its continued use on-chain (node API) because validity is purely checked against a still-valid cached credential, not against real-time revocation state.

### Likelihood Explanation
This requires the LDAP or OIDC authentication driver to be enabled (not the default `local` driver), and requires that `UpstreamSyncInterval` be configured to a non-trivial value (larger intervals increase exposure window). This is an authenticated-user-becomes-revoked scenario rather than a fully anonymous exploit, but it is a realistic operational event (offboarding an employee, compromised credential revocation) where the whole point of revocation is to be immediate.

### Recommendation
For sensitive authentication paths, avoid relying solely on cached validity windows for authorization decisions. Either:
1. Perform (rate-limited) upstream verification inline on `FindUserByAPIToken`/`FindUser` for API-token-authenticated requests, not just on the sync ticker, or
2. Reduce the default `UserAPITokenDuration`/`UpstreamSyncInterval` window and clearly document that access revocation is not immediate, and provide an explicit admin-triggered "force sync now" / "revoke all tokens for user" operation, or
3. Add a per-token or per-user monotonically increasing generation/version counter that is checked against a value pinned at token creation, incremented on any explicit revoke action, similar to solution #2 proposed in the referenced report (`batchId`).

### Proof of Concept
1. Enable LDAP authentication (`ldapCfg.UpstreamSyncInterval` set to e.g. 1h).
2. User `alice@example.com` is a member of the `EditUserGroupCN` LDAP group and creates a node API token via the normal flow, resulting in a row in `ldap_user_api_tokens`.
3. Admin removes `alice` from all LDAP role groups (revokes access) directly in the LDAP directory.
4. Before the next `LDAPServerStateSyncer.Work()` tick, `alice` sends requests to the node's `/v2/...` HTTP endpoints using her previously-issued `X-API-KEY`/`X-API-SECRET`.
5. `AuthenticateByToken` → `FindUserByAPIToken` only checks `ldap_user_api_tokens` row validity (`created_at + UserAPITokenDuration >= now()`), which is still true, so authentication succeeds and the request is processed with the cached `edit` role — despite `alice` having been fully revoked upstream.

### Citations

**File:** core/web/auth/auth.go (L78-107)
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
```

**File:** core/sessions/ldapauth/ldap.go (L1-23)
```go
/*
The LDAP authentication package forwards the credentials in the user session request
for authentication with a configured upstream LDAP server

This package relies on the two following local database tables:

	ldap_sessions: 	Upon successful LDAP response, creates a keyed local copy of the user email
	ldap_user_api_tokens: User created API tokens, tied to the node, storing user email.

Note: user can have only one API token at a time, and token expiration is enforced

User session and roles are cached and revalidated with the upstream service at the interval defined in
the local LDAP config through the Application.sessionReaper implementation in reaper.go.

Changes to the upstream identity server will propagate through and update local tables (web sessions, API tokens)
by either removing the entries or updating the roles. This sync happens for every auth endpoint hit, and
via the defined sync interval. One goroutine is created to coordinate the sync timing in the New function

This implementation is read only; user mutation actions such as Delete are not supported.

MFA is supported via the remote LDAP server implementation. Sufficient request time out should accommodate
for a blocking auth call while the user responds to a potential push notification callback.
*/
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

**File:** core/sessions/oidcauth/oidc.go (L297-338)
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
	if err != nil {
		if errors.Is(err, clsessions.ErrUserSessionExpired) {
			// API Token expired, purge
			if _, execErr := oi.ds.ExecContext(ctx, "DELETE FROM oidc_user_api_tokens WHERE token_key = $1", apiToken); execErr != nil {
				oi.lggr.Errorf("error purging stale oidc API token session: %v", execErr)
			}
		}
		return clsessions.User{}, err
	}
	return foundUser, nil
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

**File:** core/sessions/ldapauth/sync.go (L187-243)
```go
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
