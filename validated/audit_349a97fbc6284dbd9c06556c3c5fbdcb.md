### Title
Stale cached role on LDAP API tokens is not revoked when upstream group membership changes, allowing continued use of a stripped privilege until the next periodic sync - (File: core/sessions/ldapauth/ldap.go)

### Summary
CVE-2019-14902 describes Samba failing to immediately propagate the removal of a delegated ACL right to all domain controllers, letting the right stay effective on some controllers until an unrelated change forced a refresh. The chainlink LDAP auth analog is `FindUserByAPIToken`, which authorizes every API-token request purely from a locally cached `user_role` column in `ldap_user_api_tokens`, never re-checking the upstream LDAP group membership at request time.

### Finding Description
`FindUserByAPIToken` explicitly documents and implements caching of the role: "user role and email are cached so no further upstream LDAP query is performed, sessions and tokens are synced against the upstream server via the UpstreamSyncInterval config and reaper.go sync implementation" [1](#0-0) . The only mechanism that reconciles this cached role with the authoritative upstream LDAP directory is the asynchronous `LDAPServerStateSyncer.Work` job, which walks group membership and issues bulk `UPDATE ldap_user_api_tokens SET user_role = CASE ...` / deletes rows for users no longer present [2](#0-1) .

Between sync runs, an administrator who removes a user from the LDAP admin/edit/run group (revoking a privilege) has no effect on that user's already-issued API token: the token keeps authorizing at the old, higher role because `FindUserByAPIToken` reads only the locally cached `user_role` column, not upstream state [3](#0-2) . This mirrors the CVE's root cause precisely: revocation of a right is not atomically/immediately enforced everywhere it is checked — here, the "everywhere" is the two separate authorization paths (session-based `FindUser`, which does re-query LDAP live at lines 114-201, versus API-token-based `FindUserByAPIToken`, which does not).

### Impact Explanation
A demoted or offboarded user (e.g., removed from the Admin LDAP group) retains full use of their previously-issued API token at the old role for up to the configured `UpstreamSyncInterval`. Depending on that interval, this could allow continued admin-level access (fund transfers, job replay, user management via `auth.RequiresAdminRole` protected routes such as `POST /v2/users`, `DELETE /v2/users/:email`) after the operator believed access had been revoked [4](#0-3) .

### Likelihood Explanation
This requires an LDAP-authenticated deployment where a user already holds a valid, unexpired API token before their upstream role/group membership is downgraded — a plausible offboarding/role-change scenario rather than a contrived one. The window of exposure is bounded by the configured sync interval and token expiration, but is not zero, and is a genuine gap between the "declared" security state (upstream directory) and the "enforced" security state (local cache used for authorization decisions).

### Recommendation
Either (a) reduce trust in the cached role by re-validating group membership against LDAP for privileged operations, or (b) shorten/force the sync/reaper cadence so token role staleness has a bounded, documented, and configurably tight upper limit, and ensure `DeleteAuthToken`/token invalidation is triggered immediately as part of any administrative role-change/deactivation flow rather than relying solely on the background syncer.

### Proof of Concept
1. Configure LDAP auth with `UserApiTokenEnabled` and a long `UpstreamSyncInterval`.
2. As user A (LDAP Admin group member), call `CreateAndSetAuthToken` to mint an API token; it is stored with `user_role = admin` in `ldap_user_api_tokens` [5](#0-4) .
3. Remove user A from the Admin LDAP group upstream.
4. Before the next `LDAPServerStateSyncer.Work` run, use user A's still-valid API token against an admin-only endpoint; `FindUserByAPIToken` returns the stale cached `admin` role and the request is authorized [6](#0-5) .

### Citations

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

**File:** core/sessions/ldapauth/ldap.go (L544-583)
```go
// SetAuthToken updates the user to use the given Authentication Token.
func (l *ldapAuthenticator) SetAuthToken(ctx context.Context, user *sessions.User, token *auth.Token) error {
	if !l.config.UserApiTokenEnabled() {
		return errors.New("API token is not enabled ")
	}

	salt := utils.NewSecret(utils.DefaultSecretSize)
	hashedSecret, err := auth.HashedSecret(token, salt)
	if err != nil {
		return fmt.Errorf("LDAPAuth SetAuthToken hashed secret error: %w", err)
	}

	err = sqlutil.TransactDataSource(ctx, l.ds, nil, func(tx sqlutil.DataSource) error {
		// Is this user a local CLI Admin or upstream LDAP user?
		// Check presence in local users table. Set localauth_user column true if present.
		// This flag omits the session/token from being purged by the sync daemon/reaper.go
		isLocalCLIAdmin := false
		err = l.ds.QueryRowxContext(ctx, "SELECT EXISTS (SELECT 1 FROM users WHERE email = $1)", user.Email).Scan(&isLocalCLIAdmin)
		if err != nil {
			return fmt.Errorf("error checking user presence in users table: %w", err)
		}

		// Remove any existing API tokens
		if _, err = l.ds.ExecContext(ctx, "DELETE FROM ldap_user_api_tokens WHERE user_email = $1", user.Email); err != nil {
			return fmt.Errorf("error executing DELETE FROM ldap_user_api_tokens: %w", err)
		}
		// Create new API token for user
		_, err = l.ds.ExecContext(
			ctx,
			"INSERT INTO ldap_user_api_tokens (user_email, user_role, localauth_user, token_key, token_salt, token_hashed_secret, created_at) VALUES ($1, $2, $3, $4, $5, $6, now())",
			user.Email,
			user.Role,
			isLocalCLIAdmin,
			token.AccessKey,
			salt,
			hashedSecret,
		)
		if err != nil {
			return fmt.Errorf("failed insert into ldap_user_api_tokens: %w", err)
		}
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

**File:** core/web/router.go (L251-254)
```go
		authv2.GET("/users", auth.RequiresAdminRole(uc.Index))
		authv2.POST("/users", auth.RequiresAdminRole(uc.Create))
		authv2.PATCH("/users", auth.RequiresAdminRole(uc.UpdateRole))
		authv2.DELETE("/users/:email", auth.RequiresAdminRole(uc.Delete))
```
