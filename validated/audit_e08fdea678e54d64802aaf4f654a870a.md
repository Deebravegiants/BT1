Audit Report

## Title
Stale LDAP-cached role grants elevated API-token privileges after upstream demotion — ([File: core/sessions/ldapauth/ldap.go])

## Summary
`FindUserByAPIToken` in `core/sessions/ldapauth/ldap.go` authorizes API-token requests purely from the locally cached `user_role` column in the `ldap_user_api_tokens` table, without any live re-validation against the upstream LDAP server. The only mechanism that reconciles this cache with upstream group membership is the background `LDAPServerStateSyncer.Work` job, and with the documented default config value `UpstreamSyncInterval = '0s'`, that job runs only once at process startup rather than on a recurring interval — meaning a user demoted or removed from an admin/edit LDAP group upstream keeps their previously cached elevated role for the full lifetime of their API token (up to `UserAPITokenDuration`, default 240h).

## Finding Description
`FindUserByAPIToken` queries only the local database and returns the cached role without contacting LDAP: [1](#0-0) . This is the sole authorization lookup used by `AuthenticateByToken` for token-based requests: [2](#0-1) .

The cache is only corrected by `LDAPServerStateSyncer.Work`, which re-queries the upstream group membership and rewrites stored roles: [3](#0-2) . Critically, `Work` is invoked on a recurring ticker only if `UpstreamSyncInterval` is non-zero; if it is the zero/instant value — which is the documented default — `Work` is called exactly once, at startup, and never again: [4](#0-3) . This default is explicit in the shipped config docs: [5](#0-4) .

By contrast, `FindUser` (used for interactive login) performs a live LDAP group-membership query on every call: [6](#0-5) . There is no equivalent live check in the API-token path, so the package-level comment's claim that role changes "propagate through... via login/logout actions" does not hold for token-authenticated requests — only for interactive session logins that call `FindUser`, not `FindUserByAPIToken`.

The broken assumption is that cached `ldap_user_api_tokens.user_role` accurately reflects current upstream group membership at the moment of API use; in fact it is a snapshot from token creation time (or the last background sync) that can only be corrected by a periodic job that is disabled by default.

## Impact Explanation
This is an authorization/role-bypass issue: a user demoted or removed from the LDAP `Admin`/`Edit` group upstream retains full access via a previously issued API token, since `FindUserByAPIToken` returns the stale cached role rather than the current one. This maps to the in-scope "node API authentication or role bypass" impact category, and can enable unauthorized administrative actions (job/key management, run triggering) for as long as the token remains valid (up to 240h by default).

## Likelihood Explanation
Exploitation requires the LDAP authentication mode with `UserApiTokenEnabled` to be turned on (an opt-in feature, not related to attacker privilege) and a user who already holds a previously issued token to be demoted upstream. Because `UpstreamSyncInterval = '0s'` — which disables periodic resync — is the documented *default* value in `core.toml`, this is not an unusual or hardened-away-from misconfiguration; it is the out-of-the-box behavior for any LDAP-enabled deployment that doesn't explicitly override the sync interval. The demoted actor requires no admin/operator access to exploit it — they simply continue using an API token they legitimately obtained before losing privileges, which satisfies the "escalation/persistence from a previously valid, now-revoked credential" bar.

## Recommendation
- Re-validate the cached role against LDAP at read time in `FindUserByAPIToken`, or enforce a bound between `UpstreamSyncInterval`/token lifetime so a demoted user's token cannot outlive a maximum staleness window.
- Require a non-zero, periodic `UpstreamSyncInterval` whenever `UserApiTokenEnabled` is true, rather than allowing indefinite reliance on a single startup-time sync.
- Trigger synchronous revocation/role correction for `ldap_user_api_tokens` whenever `Work()` (or any live LDAP query) detects a downstream role change, instead of relying solely on the next scheduled tick.

## Proof of Concept
1. Configure `WebServer.AuthenticationMethod = 'ldap'`, `LDAP.UserApiTokenEnabled = true`, leave `LDAP.UpstreamSyncInterval` at its default `'0s'`.
2. User `alice@example.com`, a member of the upstream `NodeAdmins` LDAP group, creates an API token via the normal flow; `admin` role is cached in `ldap_user_api_tokens`.
3. Operator removes Alice from `NodeAdmins` upstream; no node restart occurs (so the one-time startup `Work()` sync doesn't rerun).
4. Alice continues calling privileged `/v2/...` endpoints with her existing API token; `AuthenticateByToken` → `FindUserByAPIToken` returns her stale cached `admin` role, granting continued admin access despite the upstream revocation, until the token naturally expires (`UserAPITokenDuration`, default 240h).

### Citations

**File:** core/sessions/ldapauth/ldap.go (L114-201)
```go
// FindUser will attempt to return an LDAP user with mapped role by email.
func (l *ldapAuthenticator) FindUser(ctx context.Context, email string) (sessions.User, error) {
	email = strings.ToLower(email)

	// First check for the supported local admin users table
	var foundLocalAdminUser sessions.User
	checkErr := l.ds.GetContext(ctx, &foundLocalAdminUser, "SELECT * FROM users WHERE lower(email) = lower($1)", email)
	if checkErr == nil {
		return foundLocalAdminUser, nil
	}
	// If error is not nil, there was either an issue or no local users found
	if !errors.Is(checkErr, sql.ErrNoRows) {
		// If the error is not that no local user was found, log and exit
		l.lggr.Errorf("error searching users table: %v", checkErr)
		return sessions.User{}, errors.New("error Finding user")
	}

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

	conn, err := l.ldapClient.CreateEphemeralConnection()
	if err != nil {
		l.lggr.Errorf("error in LDAP dial: %v", err)
		return sessions.User{}, errors.New("unable to establish connection to LDAP server with provided URL and credentials")
	}
	defer conn.Close()

	// User email and role are the only upstream data that needs queried for.
	// List query user groups using the provided email, on success is a list of group the uniquemember belongs to
	// data is readily available
	escapedEmail := ldap.EscapeFilter(email)
	searchBaseDN := fmt.Sprintf("%s, %s", l.config.GroupsDN(), l.config.BaseDN())
	filterQuery := fmt.Sprintf("(&(uniquemember=%s=%s,%s,%s))", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())
	searchRequest := ldap.NewSearchRequest(
		searchBaseDN,
		ldap.ScopeWholeSubtree, ldap.NeverDerefAliases,
		0, int(l.config.QueryTimeout().Seconds()), false,
		filterQuery,
		[]string{"cn"},
		nil,
	)

	// Query the server
	result, err := conn.Search(searchRequest)
	if err != nil {
		l.lggr.Errorf("error searching users in LDAP query: %v", err)
		return sessions.User{}, errors.New("error searching users in LDAP directory")
	}

	if len(result.Entries) == 0 {
		// Provided email is not present in upstream LDAP server, local admin CLI auth is supported
		// So query and check the users table as well before failing
		var localUserRole sessions.UserRole
		if err = l.ds.GetContext(ctx, &localUserRole, "SELECT role FROM users WHERE email = $1", email); err != nil {
			// Above query for local user unsuccessful, return error
			l.lggr.Warnf("No local users table user found with email %s", email)
			return sessions.User{}, errors.New("no users found with provided email")
		}

		// If the above query to the local users table was successful, return that local user's role
		return sessions.User{
			Email: email,
			Role:  localUserRole,
		}, nil
	}

	// Populate found user by email and role based on matched group names
	userRole, err := l.groupSearchResultsToUserRole(result.Entries)
	if err != nil {
		l.lggr.Warnf("User '%s' found but no matching assigned groups in LDAP to assume role", email)
		return sessions.User{}, err
	}

	// Convert search result to sessions.User type with required fields
	return sessions.User{
		Email: email,
		Role:  userRole,
	}, nil
```

**File:** core/sessions/ldapauth/ldap.go (L204-222)
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
```

**File:** core/web/auth/auth.go (L90-93)
```go
	}

	// We need to first load the user row so we can compare tokens using the stored salt
	user, err := authr.FindUserByAPIToken(ctx, token.AccessKey)
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

**File:** core/sessions/ldapauth/sync.go (L93-150)
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

	// Optional rate limiting check to limit the amount of upstream LDAP server queries performed
	if !l.config.UpstreamSyncRateLimit().IsInstant() {
		if !time.Now().After(l.nextSyncTime) {
			return
		}

		// Enough time has elapsed to sync again, store the time for when next sync is allowed and begin sync
		l.nextSyncTime = time.Now().Add(l.config.UpstreamSyncRateLimit().Duration())
	}

	l.lggr.Info("Begin Upstream LDAP provider state sync after checking time against config UpstreamSyncInterval and UpstreamSyncRateLimit")

	// For each defined role/group, query for the list of group members to gather the full list of possible users
	users := []sessions.User{}

	conn, err := l.ldapClient.CreateEphemeralConnection()
	if err != nil {
		l.lggr.Error("Failed to Dial LDAP Server: ", err)
		return
	}
	// Root level root user auth with credentials provided from config
	bindStr := l.config.BaseUserAttr() + "=" + l.config.ReadOnlyUserLogin() + "," + l.config.BaseDN()
	if err = conn.Bind(bindStr, l.config.ReadOnlyUserPass()); err != nil {
		l.lggr.Error("Unable to login as initial root LDAP user: ", err)
	}
	defer conn.Close()

	// Query for list of uniqueMember IDs present in Admin group
	adminUsers, err := l.ldapGroupMembersListToUser(conn, l.config.AdminUserGroupCN(), sessions.UserRoleAdmin)
	if err != nil {
		l.lggr.Error("Error in ldapGroupMembersListToUser: ", err)
		return
	}
	// Query for list of uniqueMember IDs present in Edit group
	editUsers, err := l.ldapGroupMembersListToUser(conn, l.config.EditUserGroupCN(), sessions.UserRoleEdit)
	if err != nil {
		l.lggr.Error("Error in ldapGroupMembersListToUser: ", err)
		return
	}
	// Query for list of uniqueMember IDs present in Edit group
	runUsers, err := l.ldapGroupMembersListToUser(conn, l.config.RunUserGroupCN(), sessions.UserRoleRun)
	if err != nil {
		l.lggr.Error("Error in ldapGroupMembersListToUser: ", err)
		return
	}
```

**File:** core/config/docs/core.toml (L267-270)
```text
UserAPITokenDuration = '240h0m0s' # Default
# UpstreamSyncInterval is the interval at which the background LDAP sync task will be called. A '0s' value disables the background sync being run on an interval. This check is already performed during login/logout actions, all sessions and API tokens stored in the local ldap tables are updated to match the remote server
UpstreamSyncInterval = '0s' # Default
# UpstreamSyncRateLimit defines a duration to limit the number of query/API calls to the upstream LDAP provider. It prevents the sync functionality from being called multiple times within the defined duration
```
