### Title
LDAP unauthenticated ("anonymous") bind allows authentication bypass in `CreateSession` - (`File: core/sessions/ldapauth/ldap.go`)

### Summary
`ldapAuthenticator.CreateSession` performs an LDAP simple bind using the attacker-supplied `sr.Password` without first rejecting an empty password value. Per RFC 4513, an LDAP simple bind with a non-empty DN and an empty password is defined as an **unauthenticated bind**, which many LDAP servers accept as "successful" (or fall back to anonymous access) rather than rejecting it as a failed authentication. Because this code treats `conn.Bind()` returning `nil` as proof the supplied credentials were valid, submitting any known/guessable email with an empty password string can let an unauthenticated network client obtain a valid Chainlink node session with that user's mapped role (up to Admin), i.e., a full authentication bypass.

### Finding Description
In `core/sessions/ldapauth/ldap.go`, `CreateSession` builds a bind DN from the submitted email and calls `Bind` with the raw, attacker-supplied password: [1](#0-0) 

There is no check that `sr.Password` is non-empty before this call. If the bind succeeds (`err == nil`), the code assumes the user is authenticated and proceeds to look up their role and mint a session: [2](#0-1) [3](#0-2) 

The same unguarded pattern exists in `TestPassword`, used for auth-token verification flows: [4](#0-3) 

`sessions.SessionRequest.Password` is populated directly from the unauthenticated JSON login request body (`{"email":..., "password":...}`), reachable by any network client hitting the sessions endpoint, as shown by the existing controller test that POSTs raw email/password JSON to `/sessions`: [5](#0-4) 

Because the LDAP client library (`go-ldap/v3`) simply forwards whatever password is given to the server's Bind operation, and many LDAP/AD configurations honor RFC 4513 "unauthenticated bind" semantics (treating DN + empty password as a successful, low-privilege/anonymous bind rather than an authentication failure), this is functionally analogous to the injected/loosely-validated identity input class described in CVE-2026-75007 (Roundcube's LDAP filter substitution issue): user-controlled authentication input reaches the LDAP layer without adequate validation/rejection, subverting the intended access-control decision.

### Impact Explanation
If the target LDAP/AD server has unauthenticated bind enabled (a common default or misconfiguration on many directory servers), an attacker who knows or guesses the email address of any user who is a member of an LDAP group mapped to `AdminUserGroupCN`/`EditUserGroupCN`/etc. can submit that email with an empty password and receive a valid, fully-privileged session cookie for the Chainlink node's web/API surface — a complete authentication bypass leading to unauthorized administrative access, key/job/fund-moving actions available to Admin/Edit roles.

### Likelihood Explanation
Likelihood is Medium: exploitability is fully dependent on the operator's LDAP/AD server configuration (whether unauthenticated binds are permitted) and email enumeration/guessing, both of which are common in real deployments and not something this codebase's chosen defenses (only `ldap.EscapeFilter` on search filters) address. The request itself requires no credentials and is reachable at `/sessions`, so the only barrier is the upstream directory's bind policy — something the node software should defensively guard against regardless.

### Recommendation
Explicitly reject empty (or whitespace-only) passwords before calling `conn.Bind()` in both `CreateSession` and `TestPassword`, e.g. return an authentication error immediately if `sr.Password == ""` / `password == ""`. Additionally, treat a successful `Bind` with an empty password as invalid regardless of the LDAP server's response, and consider disabling unauthenticated bind at the connection/library level if the `go-ldap` client exposes such an option.

### Proof of Concept
1. Configure `WebServer.AuthenticationMethod = 'ldap'` against a directory that permits unauthenticated binds (default on many test/prod AD/LDAP deployments).
2. Identify (or guess) the email of a user who is a member of the configured `AdminUserGroupCN` LDAP group.
3. POST to `/sessions`:
```
POST /sessions
Content-Type: application/json

{"email":"known-admin@example.com","password":""}
```
4. `CreateSession` builds `searchBaseDN` and calls `conn.Bind(searchBaseDN, "")`. The LDAP server treats this as an unauthenticated bind and returns success. `FindUser` then resolves the victim's Admin role, and a valid session cookie is issued to the unauthenticated attacker.

### Citations

**File:** core/sessions/ldapauth/ldap.go (L405-411)
```go
	// Attempt to LDAP Bind with user provided credentials
	escapedEmail := ldap.EscapeFilter(strings.ToLower(sr.Email))
	searchBaseDN := fmt.Sprintf("%s=%s,%s,%s", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())
	if err = conn.Bind(searchBaseDN, sr.Password); err != nil {
		l.lggr.Infof("Error binding user authentication request in LDAP Bind: %v", err)
		returnErr = errors.New("unable to log in with LDAP server. Check credentials")
	}
```

**File:** core/sessions/ldapauth/ldap.go (L413-420)
```go
	// Bind was successful meaning user and credentials are present in LDAP directory
	// Reuse FindUser functionality to fetch user roles used to create ldap_session entry
	// with cached user email and role
	foundUser, err := l.FindUser(ctx, escapedEmail)
	if err != nil {
		l.lggr.Infof("Successful user login, but error querying for user groups: user: %s, error %v", escapedEmail, err)
		returnErr = errors.New("log in successful, but no assigned groups to assume role")
	}
```

**File:** core/sessions/ldapauth/ldap.go (L440-456)
```go
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

**File:** core/sessions/ldapauth/ldap.go (L511-517)
```go
	// Attempt to LDAP Bind with user provided credentials
	escapedEmail := ldap.EscapeFilter(strings.ToLower(email))
	searchBaseDN := fmt.Sprintf("%s=%s,%s,%s", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())
	err = conn.Bind(searchBaseDN, password)
	if err == nil {
		return nil
	}
```

**File:** core/web/sessions_controller_test.go (L44-53)
```go
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			t.Parallel()

			ctx := t.Context()
			body := fmt.Sprintf(`{"email":"%s","password":"%s"}`, test.email, test.password)
			request, err := http.NewRequestWithContext(ctx, http.MethodPost, app.Server.URL+"/sessions", bytes.NewBufferString(body))
			require.NoError(t, err)
			resp, err := client.Do(request)
			require.NoError(t, err)
```
