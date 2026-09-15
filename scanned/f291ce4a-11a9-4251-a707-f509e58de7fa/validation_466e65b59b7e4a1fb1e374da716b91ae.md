I'll investigate whether there's an analogous access-control issue in this codebase, focusing on authentication/roles and session/token handling as legitimate areas to check.Confirmed root cause: on `Start`, the syncer performs the upstream sync immediately only `if l.config.UpstreamSyncInterval().IsInstant()` (i.e., when interval is `0s`, the *default*) at `core/sessions/ldapauth/sync.go:60-66`, and otherwise defers all subsequent syncing to a ticker at the configured interval — but crucially, once a session/token row is already cached, `AuthorizedUserWithSession` (and the OIDC/LDAP `FindUserByAPIToken` equivalents) trust the locally cached `user_role` column for the full life of that session/token, only correcting it when `Work()` runs and updates rows via the `CASE WHEN` bulk update at `core/sessions/ldapauth/sync.go:245-274`.

### Title
Stale cached role in LDAP/OIDC session and API-token tables allows demoted users to retain elevated privileges - (File: `core/sessions/ldapauth/ldap.go`, `core/sessions/oidcauth/oidc.go`, `core/sessions/ldapauth/sync.go`)

### Summary
When Chainlink is configured to use the LDAP or OIDC authentication providers, a user's role is cached locally in the `ldap_sessions`/`ldap_user_api_tokens` or `oidc_sessions`/`oidc_user_api_tokens` tables at login/token-creation time. Subsequent authorization checks (`AuthorizedUserWithSession`, `FindUserByAPIToken`) trust this cached role column directly rather than re-verifying against the live upstream group membership on every request. Refreshing the cache only happens through the periodic `LDAPServerStateSyncer`/OIDC sync `Work()` job, which is disabled by default (`UpstreamSyncInterval = '0s'`). This is analogous to CVE-2021-22176: a demoted (now lower-privileged) member continues to be treated with their prior, higher role for the remaining lifetime of their session or API token.

### Finding Description
For LDAP, `AuthorizedUserWithSession` at [1](#0-0)  reads `user_role` directly from the `ldap_sessions` row without querying the LDAP server again ("no further upstream LDAP query is performed"). The equivalent OIDC implementation at [2](#0-1)  behaves the same way for `oidc_sessions`. API tokens follow the identical pattern for `oidc_user_api_tokens` at [3](#0-2)  and for `ldap_user_api_tokens`.

The only mechanism that reconciles a demoted user's cached role with the upstream identity provider is the sync `Work()` function, which updates rows via a bulk `CASE WHEN` statement at [4](#0-3) . This sync is triggered on login/logout, and optionally on an interval — but `Start()` shows the interval-based background sync is only started `if !l.config.UpstreamSyncInterval().IsInstant()`; when the interval is the documented default of `'0s'` it is considered "instant" (disabled) and the sync runs once at node startup only: [5](#0-4) . The config documentation itself confirms: `UpstreamSyncInterval = '0s'` is the default and "disables the background sync being run on an interval" [6](#0-5) .

The net effect: if an operator demotes/removes a user from an admin/edit/run LDAP or OIDC group upstream, any of that user's already-established web sessions or long-lived API tokens (`UserAPITokenDuration` defaults to `240h`, i.e. 10 days, per [7](#0-6) ) continue to carry the old, higher cached role and continue to pass the role-gated middleware checks such as `RequiresAdminRole`/`RequiresEditRole`/`RequiresRunRole` at [8](#0-7)  and the equivalent GraphQL resolver checks at [9](#0-8) , until the session/token naturally expires (`SessionTimeout`) or the node happens to be restarted.

### Impact Explanation
A demoted user (now intended to be unprivileged for admin/edit/run-gated actions) retains their previously granted elevated role for the remaining life of their cached session or API token. Depending on the previous role, this can allow continued access to admin-only endpoints (`/v2/users`, `/v2/keys/*/import`, `/v2/keys/*/export`, `/v2/transfers*` at [10](#0-9) ), edit-role actions (bridge/external-initiator management, key creation), or run-role actions (replay, job runs) after the operator believed access was already revoked. This is a real authorization-bypass/privilege-persistence issue, though it requires that the node be configured to use LDAP or OIDC auth (not the default local auth) and that `UpstreamSyncInterval` remains at its default disabled value.

### Likelihood Explanation
Moderate-to-low: requires LDAP/OIDC auth mode configured (not default local auth), requires an operator to leave `UpstreamSyncInterval` at its default `'0s'` (which the docs describe as the default), and requires the demoted user to have an already-active, long-lived session or API token. In deployments using LDAP/OIDC with default sync settings and long `UserAPITokenDuration`/`SessionTimeout`, this window can be substantial (up to the full token/session lifetime).

### Recommendation
- Change the default `UpstreamSyncInterval` to a non-zero value so background role revalidation is always active by default, rather than relying purely on login/logout events.
- Alternatively/additionally, re-validate role against upstream (or at minimum against the local `users`-equivalent table with rate-limited freshness) on every `AuthorizedUserWithSession`/`FindUserByAPIToken` call rather than only via the periodic sync.
- Immediately invalidate/downgrade all active sessions and API tokens for a user upon detected role change, rather than waiting for the next scheduled sync.
- Document explicitly (beyond `docs/CONFIG.md`) the security implications of disabling `UpstreamSyncInterval` for LDAP/OIDC deployments.

### Proof of Concept
1. Configure Chainlink node with `LDAPAuth` (or OIDC) authentication provider and default `UpstreamSyncInterval = '0s'`.
2. User `alice` is a member of the LDAP `AdminUserGroupCN` group; she logs in, creating an `ldap_sessions` row with `user_role = 'admin'` (`core/sessions/ldapauth/ldap.go:440-452`), or issues a long-lived API token cached in `ldap_user_api_tokens` with `user_role = 'admin'`.
3. Operator removes `alice` from the upstream LDAP admin group (demotion), with no explicit forced logout/token revocation on the Chainlink node.
4. Because `UpstreamSyncInterval` is `0s` (disabled) and no login/logout event has occurred for `alice`, her cached `ldap_sessions`/`ldap_user_api_tokens` row still has `user_role = 'admin'`.
5. `alice` continues to call `RequiresAdminRole`-gated endpoints (e.g., `POST /v2/users`, `POST /v2/keys/eth/import`) using her existing session cookie or API token; `AuthorizedUserWithSession`/`FindUserByAPIToken` returns the stale cached `admin` role, and the request succeeds despite her upstream demotion.

### Citations

**File:** core/sessions/ldapauth/ldap.go (L342-373)
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

**File:** core/sessions/oidcauth/oidc.go (L349-391)
```go
// AuthorizedUserWithSession will return the API user associated with the Session ID if it
// exists and hasn't expired
func (oi *oidcAuthenticator) AuthorizedUserWithSession(ctx context.Context, sessionID string) (clsessions.User, error) {
	if len(sessionID) == 0 {
		return clsessions.User{}, errors.New("session ID cannot be empty")
	}
	var foundUser clsessions.User
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
		if !foundSession.Valid {
			// Sessions expired, purge
			return clsessions.ErrUserSessionExpired
		}
		foundUser = clsessions.User{
			Email: foundSession.UserEmail,
			Role:  foundSession.UserRole,
		}
		return nil
	})
	if err != nil {
		if errors.Is(err, clsessions.ErrUserSessionExpired) {
			if _, execErr := oi.ds.ExecContext(ctx, "DELETE FROM oidc_sessions WHERE id = $1", sessionID); execErr != nil {
				oi.lggr.Errorf("error purging stale OIDC session: %v", execErr)
			}
		}
		return clsessions.User{}, err
	}
	return foundUser, nil
}
```

**File:** core/sessions/ldapauth/sync.go (L56-67)
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
```

**File:** core/sessions/ldapauth/sync.go (L245-274)
```go
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
```

**File:** docs/CONFIG.md (L771-775)
```markdown
### UserAPITokenDuration
```toml
UserAPITokenDuration = '240h0m0s' # Default
```
UserAPITokenDuration is the duration of time an API token is active for before expiring
```

**File:** docs/CONFIG.md (L777-781)
```markdown
### UpstreamSyncInterval
```toml
UpstreamSyncInterval = '0s' # Default
```
UpstreamSyncInterval is the interval at which the background LDAP sync task will be called. A '0s' value disables the background sync being run on an interval. This check is already performed during login/logout actions, all sessions and API tokens stored in the local ldap tables are updated to match the remote server
```

**File:** core/web/auth/auth.go (L198-253)
```go
// RequiresRunRole extracts the user object from the context, and asserts the user's role is at least
// 'run'
func RequiresRunRole(handler func(*gin.Context)) func(*gin.Context) {
	return func(c *gin.Context) {
		user, ok := GetAuthenticatedUser(c)
		if !ok {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("not a valid session"))
			return
		}
		if user.Role == clsessions.UserRoleView {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("Unauthorized"))
			return
		}
		handler(c)
	}
}

// RequiresEditRole extracts the user object from the context, and asserts the user's role is at least
// 'edit'
func RequiresEditRole(handler func(*gin.Context)) func(*gin.Context) {
	return func(c *gin.Context) {
		user, ok := GetAuthenticatedUser(c)
		if !ok {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("not a valid session"))
			return
		}
		if user.Role == clsessions.UserRoleView || user.Role == clsessions.UserRoleRun {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("Unauthorized"))
			return
		}
		handler(c)
	}
}

// RequiresAdminRole extracts the user object from the context, and asserts the user's role is 'admin'
func RequiresAdminRole(handler func(*gin.Context)) func(*gin.Context) {
	return func(c *gin.Context) {
		user, ok := GetAuthenticatedUser(c)
		if !ok {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("not a valid session"))
			return
		}
		if user.Role != clsessions.UserRoleAdmin {
			c.Abort()
			addForbiddenErrorHeaders(c, "admin", string(user.Role), user.Email)
			jsonAPIError(c, http.StatusForbidden, errors.New("Forbidden"))
			return
		}
		handler(c)
	}
}
```

**File:** core/web/resolver/auth.go (L19-55)
```go
// Authenticates the user from the session cookie and asserts at least 'run' role.
func authenticateUserCanRun(ctx context.Context) error {
	session, ok := auth.GetGQLAuthenticatedSession(ctx)
	if !ok {
		return unauthorizedError{}
	}
	if session.User.Role == sessions.UserRoleView {
		return RoleNotPermittedError{session.User.Role}
	}
	return nil
}

// Authenticates the user from the session cookie and asserts at least 'edit' role.
func authenticateUserCanEdit(ctx context.Context) error {
	session, ok := auth.GetGQLAuthenticatedSession(ctx)
	if !ok {
		return unauthorizedError{}
	}
	switch session.User.Role {
	case sessions.UserRoleView, sessions.UserRoleRun:
		return RoleNotPermittedError{session.User.Role}
	default:
	}
	return nil
}

// Authenticates the user from the session cookie and asserts has 'admin' role
func authenticateUserIsAdmin(ctx context.Context) error {
	session, ok := auth.GetGQLAuthenticatedSession(ctx)
	if !ok {
		return unauthorizedError{}
	}
	if session.User.Role != sessions.UserRoleAdmin {
		return RoleNotPermittedError{session.User.Role}
	}
	return nil
}
```

**File:** core/web/router.go (L250-334)
```go
		uc := UserController{app}
		authv2.GET("/users", auth.RequiresAdminRole(uc.Index))
		authv2.POST("/users", auth.RequiresAdminRole(uc.Create))
		authv2.PATCH("/users", auth.RequiresAdminRole(uc.UpdateRole))
		authv2.DELETE("/users/:email", auth.RequiresAdminRole(uc.Delete))
		authv2.PATCH("/user/password", uc.UpdatePassword)
		authv2.POST("/user/token", uc.NewAPIToken)
		authv2.POST("/user/token/delete", uc.DeleteAPIToken)

		wa := NewWebAuthnController(app)
		authv2.GET("/enroll_webauthn", wa.BeginRegistration)
		authv2.POST("/enroll_webauthn", wa.FinishRegistration)

		eia := ExternalInitiatorsController{app}
		authv2.GET("/external_initiators", paginatedRequest(eia.Index))
		authv2.POST("/external_initiators", auth.RequiresEditRole(eia.Create))
		authv2.DELETE("/external_initiators/:Name", auth.RequiresEditRole(eia.Destroy))

		bt := BridgeTypesController{app}
		authv2.GET("/bridge_types", paginatedRequest(bt.Index))
		authv2.POST("/bridge_types", auth.RequiresEditRole(bt.Create))
		authv2.GET("/bridge_types/:BridgeName", bt.Show)
		authv2.PATCH("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Update))
		authv2.DELETE("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Destroy))

		ets := EVMTransfersController{app}
		authv2.POST("/transfers", auth.RequiresAdminRole(ets.Create))
		authv2.POST("/transfers/evm", auth.RequiresAdminRole(ets.Create))
		tts := CosmosTransfersController{app}
		authv2.POST("/transfers/cosmos", auth.RequiresAdminRole(tts.Create))
		sts := SolanaTransfersController{app}
		authv2.POST("/transfers/solana", auth.RequiresAdminRole(sts.Create))

		cc := ConfigController{app}
		authv2.GET("/config", cc.Show)
		authv2.GET("/config/v2", cc.Show)

		tas := TxAttemptsController{app}
		authv2.GET("/tx_attempts", paginatedRequest(tas.Index))
		authv2.GET("/tx_attempts/evm", paginatedRequest(tas.Index))

		txs := TransactionsController{app}
		authv2.GET("/transactions/evm", paginatedRequest(txs.Index))
		authv2.GET("/transactions/evm/:TxHash", txs.Show)
		authv2.GET("/transactions", paginatedRequest(txs.Index))
		authv2.GET("/transactions/:TxHash", txs.Show)

		rc := ReplayController{app}
		authv2.POST("/replay_from_block/:number", auth.RequiresRunRole(rc.ReplayFromBlock))
		lcaC := LCAController{app}
		authv2.GET("/find_lca", auth.RequiresRunRole(lcaC.FindLCA))
		lpSkipC := LPSkipController{app}
		authv2.POST("/lp_skip_to_block", auth.RequiresRunRole(lpSkipC.LPSkipToBlock))

		if build.IsDev() {
			capContr := CapabilityController{app}
			authv2.POST("/execute_capability", auth.RequiresRunRole(capContr.ExecuteCapability))
		}

		csakc := CSAKeysController{app}
		authv2.GET("/keys/csa", csakc.Index)
		authv2.POST("/keys/csa", auth.RequiresEditRole(csakc.Create))
		authv2.POST("/keys/csa/import", auth.RequiresAdminRole(csakc.Import))
		authv2.POST("/keys/csa/export/:ID", auth.RequiresAdminRole(csakc.Export))

		ekc := NewETHKeysController(app)
		authv2.GET("/keys/eth", ekc.Index)
		authv2.POST("/keys/eth", auth.RequiresEditRole(ekc.Create))
		authv2.DELETE("/keys/eth/:keyID", auth.RequiresAdminRole(ekc.Delete))
		authv2.POST("/keys/eth/import", auth.RequiresAdminRole(ekc.Import))
		authv2.POST("/keys/eth/export/:address", auth.RequiresAdminRole(ekc.Export))
		// duplicated from above, with `evm` instead of `eth`
		// legacy ones remain for backwards compatibility

		ethKeysGroup := authv2.Group("", auth.Authenticate(app.AuthenticationProvider(),
			auth.AuthenticateByToken,
			auth.AuthenticateBySession,
		))

		ethKeysGroup.Use(ekc.formatETHKeyResponse())
		authv2.GET("/keys/evm", ekc.Index)
		ethKeysGroup.POST("/keys/evm", auth.RequiresEditRole(ekc.Create))
		ethKeysGroup.DELETE("/keys/evm/:address", auth.RequiresAdminRole(ekc.Delete))
		ethKeysGroup.POST("/keys/evm/import", auth.RequiresAdminRole(ekc.Import))
		authv2.POST("/keys/evm/export/:address", auth.RequiresAdminRole(ekc.Export))
```
